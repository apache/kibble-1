# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import multiprocessing
import threading
import time
from typing import List

from kibble.configuration import conf
from kibble.scanners.brokers import kibbleES

PENDING_OBJECTS = []
BIG_LOCK = threading.Lock()


def is_mine(id_):
    balance = conf.get("scanner", "balance")
    if not balance:
        return False
    node_no, num_nodes = balance.split("/")
    node_no, num_nodes = int(node_no), int(num_nodes)
    if num_nodes == 0:
        return True
    bignum = int(id_, 16) % num_nodes
    if bignum == node_no - 1:
        return True
    return False


class ScanThread(threading.Thread):
    """
    A thread object that grabs an item from the queue and processes
    it, using whatever plugins will come out to play.
    """

    def __init__(self, broker, org, i, t=None, e=None):
        super(ScanThread, self).__init__()
        self.broker = broker
        self.org = org
        self.id = i
        self.bit = self.broker.bitClass(self.broker, self.org, i)
        self.stype = t
        self.exclude = e
        print("Initialized thread %i" % i)

    def run(self):
        from kibble.scanners import scanners

        global BIG_LOCK, PENDING_OBJECTS
        time.sleep(0.5)  # Primarily to align printouts.
        # While there are objects to snag
        while PENDING_OBJECTS:
            BIG_LOCK.acquire(blocking=True)
            try:
                # Try grabbing an object (might not be any left!)
                obj = PENDING_OBJECTS.pop(0)
                # If load balancing jobs, make sure this one is ours
                if is_mine(obj["sourceID"]):
                    # Run through list of scanners in order, apply when useful
                    for sid, scanner in scanners.enumerate():
                        if scanner.accepts(obj):
                            self.bit.pluginname = "plugins/scanners/" + sid
                            # Excluded scanner type?
                            if self.exclude and sid in self.exclude:
                                continue
                            # Specific scanner type or no types mentioned?
                            if not self.stype or self.stype == sid:
                                scanner.scan(self.bit, obj)
            except:
                break
            finally:
                BIG_LOCK.release()
        self.bit.pluginname = "core"
        self.bit.pprint("No more objects, exiting!")


def scan_cmd(
    scanners: List[str] = None,
    exclude: List[str] = None,
    org: str = None,
    age: int = None,
    source: str = None,
    view: str = None,
):
    global PENDING_OBJECTS

    print(f"Kibble Scanner starting")
    print("Using direct ElasticSearch broker model")
    broker = kibbleES.Broker()

    org_no = 0
    source_no = 0
    for org_item in broker.organisations():
        if not org or org == org_item.id:
            print("Processing organisation %s" % org_item.id)
            org_no += 1

            # Compile source list
            # If --age is passed, only append source that either
            # have never been scanned, or have been scanned more than
            # N hours ago by any scanner.
            if age:
                minAge = time.time() - int(age) * 3600
                for source_item in org_item.sources(view=view):
                    tooNew = False
                    if "steps" in source_item:
                        for _, step in source_item["steps"].items():
                            if "time" in step and step["time"] >= minAge:
                                tooNew = True
                                break
                    if not tooNew:
                        if not source or (source == source_item["sourceID"]):
                            PENDING_OBJECTS.append(source)
            else:
                PENDING_OBJECTS = []
                for source_item in org_item.sources(view=view):
                    if not source or (source == source_item["sourceID"]):
                        PENDING_OBJECTS.append(source_item)
                source_no += len(PENDING_OBJECTS)

            # Start up some threads equal to number of cores on the box,
            # but no more than 4. We don't want an IOWait nightmare.
            threads = []
            core_count = min((4, int(multiprocessing.cpu_count())))
            for i in range(1, core_count):
                s_thread = ScanThread(broker, org_item, i + 1, scanners, exclude)
                s_thread.start()
                threads.append(s_thread)

            # Wait for them all to finish.
            for t in threads:
                t.join()

    print(
        f"All done scanning for now, found {org_no} organisations and {source_no} sources to process."
    )

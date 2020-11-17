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

import argparse
import multiprocessing
import os
import threading
import time
from pprint import pprint

import yaml

from kibble.scanners import scanners
from kibble.scanners.brokers import kibbleES

VERSION = "0.1.0"
CONFIG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.yaml")
PENDING_OBJECTS = []
BIG_LOCK = threading.Lock()


def base_parser():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "-o",
        "--org",
        help="The organisation to gather stats for. If left out, all organisations will be scanned.",
    )
    arg_parser.add_argument(
        "-f", "--config", help="Location of the yaml config file (full path)"
    )
    arg_parser.add_argument(
        "-a",
        "--age",
        help="Minimum age in hours before performing a new scan on an already processed source. --age 12 will not process any source that was processed less than 12 hours ago, but will process new sources.",
    )
    arg_parser.add_argument(
        "-s", "--source", help="A specific source (wildcard) to run scans on."
    )
    arg_parser.add_argument(
        "-n", "--nodes", help="Number of nodes in the cluster (used for load balancing)"
    )
    arg_parser.add_argument(
        "-t",
        "--type",
        help="Specific type of scanner to run (default is run all scanners)",
    )
    arg_parser.add_argument(
        "-e", "--exclude", nargs="+", help="Specific type of scanner(s) to exclude"
    )
    arg_parser.add_argument(
        "-v",
        "--view",
        help="Specific source view to scan (default is scan all sources)",
    )
    return arg_parser


def isMine(ID, config):
    if config["scanner"].get("balance", None):
        a = config["scanner"]["balance"].split("/")
        nodeNo = int(a[0])
        numNodes = int(a[1])
        if numNodes == 0:
            return True
        bignum = int(ID, 16) % numNodes
        if bignum == int(nodeNo) - 1:
            return True
        return False
    return True


class scanThread(threading.Thread):
    """ A thread object that grabs an item from the queue and processes
        it, using whatever plugins will come out to play. """

    def __init__(self, broker, org, i, t=None, e=None):
        super(scanThread, self).__init__()
        self.broker = broker
        self.org = org
        self.id = i
        self.bit = self.broker.bitClass(self.broker, self.org, i)
        self.stype = t
        self.exclude = e
        pprint("Initialized thread %i" % i)

    def run(self):
        global BIG_LOCK, PENDING_OBJECTS
        time.sleep(0.5)  # Primarily to align printouts.
        # While there are objects to snag
        a = 0
        while PENDING_OBJECTS:
            BIG_LOCK.acquire(blocking=True)
            try:
                # Try grabbing an object (might not be any left!)
                obj = PENDING_OBJECTS.pop(0)
            except:
                pass
            BIG_LOCK.release()
            if obj:
                # If load balancing jobs, make sure this one is ours
                if isMine(obj["sourceID"], self.broker.config):
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
            else:
                break
        self.bit.pluginname = "core"
        self.bit.pprint("No more objects, exiting!")


def main():
    pprint("Kibble Scanner v/%s starting" % VERSION)
    global CONFIG_FILE, PENDING_OBJECTS
    args = base_parser().parse_args()

    # Load config yaml
    if args.config:
        CONFIG_FILE = args.config
    config = yaml.load(open(CONFIG_FILE))
    pprint("Loaded YAML config from %s" % CONFIG_FILE)

    pprint("Using direct ElasticSearch broker model")
    broker = kibbleES.Broker(config)

    orgNo = 0
    sourceNo = 0
    for org in broker.organisations():
        if not args.org or args.org == org.id:
            pprint("Processing organisation %s" % org.id)
            orgNo += 1

            # Compile source list
            # If --age is passed, only append source that either
            # have never been scanned, or have been scanned more than
            # N hours ago by any scanner.
            if args.age:
                minAge = time.time() - int(args.age) * 3600
                for source in org.sources(view=args.view):
                    tooNew = False
                    if "steps" in source:
                        for key, step in source["steps"].items():
                            if "time" in step and step["time"] >= minAge:
                                tooNew = True
                                break
                    if not tooNew:
                        if not args.source or (args.source == source["sourceID"]):
                            PENDING_OBJECTS.append(source)
            else:
                PENDING_OBJECTS = []
                for source in org.sources(view=args.view):
                    if not args.source or (args.source == source["sourceID"]):
                        PENDING_OBJECTS.append(source)
                sourceNo += len(PENDING_OBJECTS)

            # Start up some threads equal to number of cores on the box,
            # but no more than 4. We don't want an IOWait nightmare.
            threads = []
            core_count = min((4, int(multiprocessing.cpu_count())))
            for i in range(0, core_count):
                sThread = scanThread(broker, org, i + 1, args.type, args.exclude)
                sThread.start()
                threads.append(sThread)

            # Wait for them all to finish.
            for t in threads:
                t.join()

    pprint(
        "All done scanning for now, found %i organisations and %i sources to process."
        % (orgNo, sourceNo)
    )


if __name__ == "__main__":
    main()

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

import datetime
import hashlib
import re
import threading
import time

from kibble.scanners.utils import jsonapi

"""
This is the Kibble Buildbot scanner plugin.
"""

title = "Scanner for Buildbot"
version = "0.1.0"


def accepts(source):
    """ Determines whether we want to handle this source """
    if source["type"] == "buildbot":
        return True
    return False


def scanJob(KibbleBit, source, job, creds):
    """ Scans a single job for activity """
    dhash = hashlib.sha224(
        ("%s-%s-%s" % (source["organisation"], source["sourceID"], job)).encode(
            "ascii", errors="replace"
        )
    ).hexdigest()
    doc = None
    found = KibbleBit.exists("cijob", dhash)

    jobURL = "%s/json/builders/%s/builds/_all" % (source["sourceURL"], job)
    KibbleBit.pprint(jobURL)
    jobjson = jsonapi.get(jobURL, auth=creds)

    # If valid JSON, ...
    if jobjson:
        for buildno, data in jobjson.items():
            buildhash = hashlib.sha224(
                (
                    "%s-%s-%s-%s"
                    % (source["organisation"], source["sourceID"], job, buildno)
                ).encode("ascii", errors="replace")
            ).hexdigest()
            builddoc = None
            try:
                builddoc = KibbleBit.get("ci_build", buildhash)
            except:
                pass

            # If this build already completed, no need to parse it again
            if builddoc and builddoc.get("completed", False):
                continue

            KibbleBit.pprint(
                "[%s-%s] This is new or pending, analyzing..." % (job, buildno)
            )

            completed = True if "currentStep" in data else False

            # Get build status (success, failed, canceled etc)
            status = "building"
            if "successful" in data.get("text", []):
                status = "success"
            if "failed" in data.get("text", []):
                status = "failed"
            if "exception" in data.get("text", []):
                status = "aborted"

            DUR = 0
            # Calc when the build finished
            if completed and len(data.get("times", [])) == 2 and data["times"][1]:
                FIN = data["times"][1]
                DUR = FIN - data["times"][0]
            else:
                FIN = 0

            doc = {
                # Build specific data
                "id": buildhash,
                "date": time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(FIN)),
                "buildID": buildno,
                "completed": completed,
                "duration": DUR * 1000,  # Buildbot does seconds, not milis
                "job": job,
                "jobURL": "%s/builders/%s" % (source["sourceURL"], job),
                "status": status,
                "started": int(data["times"][0]),
                "ci": "buildbot",
                # Standard docs values
                "sourceID": source["sourceID"],
                "organisation": source["organisation"],
                "upsert": True,
            }
            KibbleBit.append("ci_build", doc)
        # Yay, it worked!
        return True

    # Boo, it failed!
    KibbleBit.pprint("Fetching job data failed!")
    return False


class buildbotThread(threading.Thread):
    """ Generic thread class for scheduling multiple scans at once """

    def __init__(self, block, KibbleBit, source, creds, jobs):
        super(buildbotThread, self).__init__()
        self.block = block
        self.KibbleBit = KibbleBit
        self.creds = creds
        self.source = source
        self.jobs = jobs

    def run(self):
        badOnes = 0
        while len(self.jobs) > 0 and badOnes <= 50:
            self.block.acquire()
            try:
                job = self.jobs.pop(0)
            except Exception:
                self.block.release()
                return
            if not job:
                self.block.release()
                return
            self.block.release()
            if not scanJob(self.KibbleBit, self.source, job, self.creds):
                self.KibbleBit.pprint("[%s] This borked, trying another one" % job)
                badOnes += 1
                if badOnes > 100:
                    self.KibbleBit.pprint("Too many errors, bailing!")
                    self.source["steps"]["ci"] = {
                        "time": time.time(),
                        "status": "Too many errors while parsing at "
                        + time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(time.time())),
                        "running": False,
                        "good": False,
                    }
                    self.KibbleBit.updateSource(self.source)
                    return
            else:
                badOnes = 0


def scan(KibbleBit, source):
    # Simple URL check
    buildbot = re.match(r"(https?://.+)", source["sourceURL"])
    if buildbot:

        source["steps"]["ci"] = {
            "time": time.time(),
            "status": "Parsing Buildbot job changes...",
            "running": True,
            "good": True,
        }
        KibbleBit.updateSource(source)

        KibbleBit.pprint("Parsing Buildbot activity at %s" % source["sourceURL"])
        source["steps"]["ci"] = {
            "time": time.time(),
            "status": "Downloading changeset",
            "running": True,
            "good": True,
        }
        KibbleBit.updateSource(source)

        # Buildbot may neeed credentials
        creds = None
        if (
            source["creds"]
            and "username" in source["creds"]
            and source["creds"]["username"]
            and len(source["creds"]["username"]) > 0
        ):
            creds = "%s:%s" % (source["creds"]["username"], source["creds"]["password"])

        # Get the job list
        sURL = source["sourceURL"]
        KibbleBit.pprint("Getting job list...")
        builders = jsonapi.get("%s/json/builders" % sURL, auth=creds)

        # Save queue snapshot
        NOW = int(datetime.datetime.utcnow().timestamp())
        queuehash = hashlib.sha224(
            (
                "%s-%s-queue-%s"
                % (source["organisation"], source["sourceID"], int(time.time()))
            ).encode("ascii", errors="replace")
        ).hexdigest()

        # Scan queue items
        blocked = 0
        stuck = 0
        queueSize = 0
        actualQueueSize = 0
        building = 0
        jobs = []

        for builder, data in builders.items():
            jobs.append(builder)
            if data["state"] == "building":
                building += 1
            if data.get("pendingBuilds", 0) > 0:
                # All queued items, even offlined builders
                actualQueueSize += data.get("pendingBuilds", 0)
                # Only queues with an online builder (actually waiting stuff)
                if data["state"] == "building":
                    queueSize += data.get("pendingBuilds", 0)
                    blocked += data.get("pendingBuilds", 0)  # Blocked by running builds
                # Stuck builds (iow no builder available)
                if data["state"] == "offline":
                    stuck += data.get("pendingBuilds", 0)

        # Write up a queue doc
        queuedoc = {
            "id": queuehash,
            "date": time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(NOW)),
            "time": NOW,
            "size": queueSize,
            "blocked": blocked,
            "stuck": stuck,
            "building": building,
            "ci": "buildbot",
            # Standard docs values
            "sourceID": source["sourceID"],
            "organisation": source["organisation"],
            "upsert": True,
        }
        KibbleBit.append("ci_queue", queuedoc)

        KibbleBit.pprint("Found %u builders in Buildbot" % len(jobs))

        threads = []
        block = threading.Lock()
        KibbleBit.pprint("Scanning jobs using 4 sub-threads")
        for i in range(0, 4):
            t = buildbotThread(block, KibbleBit, source, creds, jobs)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # We're all done, yaay
        KibbleBit.pprint("Done scanning %s" % source["sourceURL"])

        source["steps"]["ci"] = {
            "time": time.time(),
            "status": "Buildbot successfully scanned at "
            + time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(time.time())),
            "running": False,
            "good": True,
        }
        KibbleBit.updateSource(source)

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

import requests
import requests.exceptions

"""
This is the Kibble Travis CI scanner plugin.
"""

title = "Scanner for Travis CI"
version = "0.1.0"


def accepts(source):
    """ Determines whether we want to handle this source """
    if source["type"] == "travis":
        return True
    return False


def scanJob(KibbleBit, source, bid, token, TLD):
    """ Scans a single job for activity """
    # NOW = int(datetime.datetime.utcnow().timestamp())
    dhash = hashlib.sha224(
        ("%s-%s-%s" % (source["organisation"], source["sourceURL"], bid)).encode(
            "ascii", errors="replace"
        )
    ).hexdigest()

    # Get the job data
    pages = 0
    offset = 0
    last_page = False
    oURL = "https://api.travis-ci.%s/repo/%s/builds" % (TLD, bid)

    # For as long as pagination makes sense...
    while not last_page:
        bURL = "https://api.travis-ci.%s/repo/%s/builds?limit=100&offset=%u" % (
            TLD,
            bid,
            offset,
        )
        KibbleBit.pprint("Scanning %s" % bURL)
        rv = requests.get(
            bURL,
            headers={"Travis-API-Version": "3", "Authorization": "token %s" % token},
        )
        if rv.status_code == 200:
            repojs = rv.json()
            # If travis tells us it's the last page, trust it.
            if repojs["@pagination"]["is_last"]:
                KibbleBit.pprint(
                    "Assuming this is the last page we need (travis says so)"
                )
                last_page = True

            KibbleBit.pprint(
                "%s has %u builds done" % (bURL, repojs["@pagination"]["count"])
            )

            # BREAKER: If we go past count somehow, and travis doesn't say so, bork anyway
            if repojs["@pagination"]["count"] < offset:
                return True

            offset += 100
            for build in repojs.get("builds", []):
                buildID = build["id"]
                buildProject = build["repository"]["slug"]
                startedAt = build["started_at"]
                finishedAt = build["finished_at"]
                duration = build["duration"]
                completed = True if duration else False
                duration = duration or 0

                buildhash = hashlib.sha224(
                    (
                        "%s-%s-%s-%s"
                        % (source["organisation"], source["sourceURL"], bid, buildID)
                    ).encode("ascii", errors="replace")
                ).hexdigest()
                builddoc = None
                try:
                    builddoc = KibbleBit.get("ci_build", buildhash)
                except:
                    pass

                # If this build already completed, no need to parse it again
                if builddoc and builddoc.get("completed", False):
                    # If we're on page > 1 and we've seen a completed build, assume
                    # that we don't need the older ones
                    if pages > 1:
                        KibbleBit.pprint(
                            "Assuming this is the last page we need (found completed build on page > 1)"
                        )
                        last_page = True
                        break
                    continue

                # Get build status (success, failed, canceled etc)
                status = "building"
                if build["state"] in ["finished", "passed"]:
                    status = "success"
                if build["state"] in ["failed", "errored"]:
                    status = "failed"
                if build["state"] in ["aborted", "canceled"]:
                    status = "aborted"

                FIN = 0
                STA = 0
                if finishedAt:
                    FIN = datetime.datetime.strptime(
                        finishedAt, "%Y-%m-%dT%H:%M:%SZ"
                    ).timestamp()
                if startedAt:
                    STA = int(
                        datetime.datetime.strptime(
                            startedAt, "%Y-%m-%dT%H:%M:%SZ"
                        ).timestamp()
                    )

                # We don't know how to calc queues yet, set to 0
                queuetime = 0

                doc = {
                    # Build specific data
                    "id": buildhash,
                    "date": time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(FIN)),
                    "buildID": buildID,
                    "completed": completed,
                    "duration": duration * 1000,
                    "job": buildProject,
                    "jobURL": oURL,
                    "status": status,
                    "started": STA,
                    "ci": "travis",
                    "queuetime": queuetime,
                    # Standard docs values
                    "sourceID": source["sourceID"],
                    "organisation": source["organisation"],
                    "upsert": True,
                }
                KibbleBit.append("ci_build", doc)
            pages += 1
        else:
            # We hit a snag, abort!
            KibbleBit.pprint("Travis returned a non-200 response, aborting.")
            return False

    return True


class travisThread(threading.Thread):
    """ Generic thread class for scheduling multiple scans at once """

    def __init__(self, block, KibbleBit, source, token, jobs, TLD):
        super(travisThread, self).__init__()
        self.block = block
        self.KibbleBit = KibbleBit
        self.token = token
        self.source = source
        self.jobs = jobs
        self.tld = TLD

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
            if not scanJob(self.KibbleBit, self.source, job, self.token, self.tld):
                self.KibbleBit.pprint("[%s] This borked, trying another one" % job)
                badOnes += 1
                if badOnes > 100:
                    self.KibbleBit.pprint("Too many errors, bailing!")
                    self.source["steps"]["travis"] = {
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


def sclan(KibbleBit, source):
    # Simple URL check
    travis = re.match(r"https?://travis-ci\.(org|com)", source["sourceURL"])
    if travis:
        # Is this travs-ci.org or travis-ci.com - we need to know!
        TLD = travis.group(1)
        source["steps"]["travis"] = {
            "time": time.time(),
            "status": "Parsing Travis job changes...",
            "running": True,
            "good": True,
        }
        KibbleBit.updateSource(source)

        pendingJobs = []
        KibbleBit.pprint("Parsing Travis activity at %s" % source["sourceURL"])
        source["steps"]["travis"] = {
            "time": time.time(),
            "status": "Downloading changeset",
            "running": True,
            "good": True,
        }
        KibbleBit.updateSource(source)

        # Travis needs a token
        token = None
        if (
            source["creds"]
            and "token" in source["creds"]
            and source["creds"]["token"]
            and len(source["creds"]["token"]) > 0
        ):
            token = source["creds"]["token"]
        else:
            KibbleBit.pprint("Travis CI requires a token to work!")
            return False

        # Used for pagination
        jobs = 100
        offset = 0

        # Counters; builds queued, running and total jobs
        queued = 0  # We don't know how to count this yet
        building = 0
        total = 0
        blocked = 0  # Dunno how to count yet
        stuck = 0  # Ditto
        avgqueuetime = 0  # Ditto, fake it

        maybeQueued = []
        while jobs == 100:
            URL = (
                "https://api.travis-ci.%s/repos?repository.active=true&sort_by=current_build:desc&offset=%u&limit=100&include=repository.last_started_build"
                % (TLD, offset)
            )
            offset += 100
            r = requests.get(
                URL,
                headers={
                    "Travis-API-Version": "3",
                    "Authorization": "token %s" % token,
                },
            )

            if r.status_code != 200:
                KibbleBit.pprint("Travis did not return a 200 Okay, bad token?!")

                source["steps"]["travis"] = {
                    "time": time.time(),
                    "status": "Travis CI scan failed at "
                    + time.strftime(
                        "%Y/%m/%d %H:%M:%S", time.gmtime(time.time()) + ". Bad token??!"
                    ),
                    "running": False,
                    "good": False,
                }
                KibbleBit.updateSource(source)
                return

            # For each build job
            js = r.json()
            for repo in js["repositories"]:
                total += 1
                cb = repo.get("last_started_build")
                if cb:
                    # Is the build currently running?
                    if cb["state"] in ["started", "created", "queued", "pending"]:
                        for job in cb.get("jobs", []):
                            maybeQueued.append(job["id"])

                # Queue up build jobs for the threaded scanner
                bid = repo["id"]
                pendingJobs.append(bid)

            jobs = len(js["repositories"])
            KibbleBit.pprint("Scanned %u jobs..." % total)

        # Find out how many building and pending jobs
        for jobID in maybeQueued:
            URL = "https://api.travis-ci.%s/job/%u" % (TLD, jobID)
            r = requests.get(
                URL,
                headers={
                    "Travis-API-Version": "3",
                    "Authorization": "token %s" % token,
                },
            )
            if r.status_code == 200:
                jobjs = r.json()
                if jobjs["state"] == "started":
                    building += 1
                    KibbleBit.pprint("Job %u is building" % jobID)
                elif jobjs["state"] in ["created", "queued", "pending"]:
                    queued += 1
                    blocked += 1  # Queued in Travis generally means a job can't find an executor, and thus is blocked.
                    KibbleBit.pprint("Job %u is pending" % jobID)
        KibbleBit.pprint("%u building, %u queued..." % (building, queued))

        # Save queue snapshot
        NOW = int(datetime.datetime.utcnow().timestamp())
        queuehash = hashlib.sha224(
            (
                "%s-%s-queue-%s"
                % (source["organisation"], source["sourceURL"], int(time.time()))
            ).encode("ascii", errors="replace")
        ).hexdigest()

        # Write up a queue doc
        queuedoc = {
            "id": queuehash,
            "date": time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(NOW)),
            "time": NOW,
            "building": building,
            "size": queued,
            "blocked": blocked,
            "stuck": stuck,
            "avgwait": avgqueuetime,
            "ci": "travis",
            # Standard docs values
            "sourceID": source["sourceID"],
            "organisation": source["organisation"],
            "upsert": True,
        }
        KibbleBit.append("ci_queue", queuedoc)

        KibbleBit.pprint("Found %u jobs in Travis" % len(pendingJobs))

        threads = []
        block = threading.Lock()
        KibbleBit.pprint("Scanning jobs using 4 sub-threads")
        for i in range(0, 4):
            t = travisThread(block, KibbleBit, source, token, pendingJobs, TLD)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # We're all done, yaay
        KibbleBit.pprint("Done scanning %s" % source["sourceURL"])

        source["steps"]["travis"] = {
            "time": time.time(),
            "status": "Travis successfully scanned at "
            + time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(time.time())),
            "running": False,
            "good": True,
        }
        KibbleBit.updateSource(source)

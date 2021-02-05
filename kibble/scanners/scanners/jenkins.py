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
import urllib.parse

from kibble.scanners.utils import jsonapi

"""
This is the Kibble Jenkins scanner plugin.
"""

title = "Scanner for Jenkins CI"
version = "0.1.0"


def accepts(source):
    """ Determines whether we want to handle this source """
    if source["type"] == "jenkins":
        return True
    return False


def scan_job(kibble_bit, source, job, creds):
    """ Scans a single job for activity """
    NOW = int(datetime.datetime.utcnow().timestamp())
    jname = job["name"]
    if job.get("folder"):
        jname = job.get("folder") + "-" + job["name"]
    dhash = hashlib.sha224(
        ("%s-%s-%s" % (source["organisation"], source["sourceURL"], jname)).encode(
            "ascii", errors="replace"
        )
    ).hexdigest()

    # Get $jenkins/job/$job-name/json...
    job_url = (
        "%s/api/json?depth=2&tree=builds[number,status,timestamp,id,result,duration]"
        % job["fullURL"]
    )
    kibble_bit.pprint(job_url)
    jobjson = jsonapi.get(job_url, auth=creds)

    # If valid JSON, ...
    if jobjson:
        for build in jobjson.get("builds", []):
            buildhash = hashlib.sha224(
                (
                    "%s-%s-%s-%s"
                    % (source["organisation"], source["sourceURL"], jname, build["id"])
                ).encode("ascii", errors="replace")
            ).hexdigest()
            builddoc = None
            try:
                builddoc = kibble_bit.get("ci_build", buildhash)
            except:  # pylint: disable=bare-except
                pass

            # If this build already completed, no need to parse it again
            if builddoc and builddoc.get("completed", False):
                continue

            kibble_bit.pprint(
                "[%s-%s] This is new or pending, analyzing..." % (jname, build["id"])
            )

            completed = True if build["result"] else False

            # Estimate time spent in queue
            queuetime = 0
            TS = int(build["timestamp"] / 1000)
            if builddoc:
                queuetime = builddoc.get("queuetime", 0)
            if not completed:
                queuetime = NOW - TS

            # Get build status (success, failed, canceled etc)
            status = "building"
            if build["result"] in ["SUCCESS", "STABLE"]:
                status = "success"
            if build["result"] in ["FAILURE", "UNSTABLE"]:
                status = "failed"
            if build["result"] in ["ABORTED"]:
                status = "aborted"

            # Calc when the build finished (jenkins doesn't show this)
            if completed:
                FIN = int(build["timestamp"] + build["duration"]) / 1000
            else:
                FIN = 0

            doc = {
                # Build specific data
                "id": buildhash,
                "date": time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(FIN)),
                "buildID": build["id"],
                "completed": completed,
                "duration": build["duration"],
                "job": jname,
                "job_url": job_url,
                "status": status,
                "started": int(build["timestamp"] / 1000),
                "ci": "jenkins",
                "queuetime": queuetime,
                # Standard docs values
                "sourceID": source["sourceID"],
                "organisation": source["organisation"],
                "upsert": True,
            }
            kibble_bit.append("ci_build", doc)
        # Yay, it worked!
        return True

    # Boo, it failed!
    kibble_bit.pprint("Fetching job data failed!")
    return False


class Jenkinsthread(threading.Thread):
    """ Generic thread class for scheduling multiple scans at once """

    def __init__(self, block, KibbleBit, source, creds, jobs):
        super(Jenkinsthread, self).__init__()
        self.block = block
        self.KibbleBit = KibbleBit
        self.creds = creds
        self.source = source
        self.jobs = jobs

    def run(self):
        bad_ones = 0
        while len(self.jobs) > 0 and bad_ones <= 50:
            self.block.acquire()
            try:
                job = self.jobs.pop(0)
            except Exception as err:
                print(f"An error occurred: {err}")
                self.block.release()
                return
            if not job:
                self.block.release()
                return
            self.block.release()
            jfolder = job.get("folder")
            ssource = dict(self.source)
            if jfolder:
                ssource["sourceURL"] += "/job/" + jfolder
            if not scan_job(self.KibbleBit, ssource, job, self.creds):
                self.KibbleBit.pprint(
                    "[%s] This borked, trying another one" % job["name"]
                )
                bad_ones += 1
                if bad_ones > 100:
                    self.KibbleBit.pprint("Too many errors, bailing!")
                    self.source["steps"]["issues"] = {
                        "time": time.time(),
                        "status": "Too many errors while parsing at "
                        + time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(time.time())),
                        "running": False,
                        "good": False,
                    }
                    self.KibbleBit.update_source(self.source)
                    return
            else:
                bad_ones = 0


def scan(kibble_bit, source):
    # Simple URL check
    jenkins = re.match(r"(https?://.+)", source["sourceURL"])
    if jenkins:

        source["steps"]["jenkins"] = {
            "time": time.time(),
            "status": "Parsing Jenkins job changes...",
            "running": True,
            "good": True,
        }
        kibble_bit.update_source(source)

        kibble_bit.pprint("Parsing Jenkins activity at %s" % source["sourceURL"])
        source["steps"]["issues"] = {
            "time": time.time(),
            "status": "Downloading changeset",
            "running": True,
            "good": True,
        }
        kibble_bit.update_source(source)

        # Jenkins may neeed credentials
        creds = None
        if (
            source["creds"]
            and "username" in source["creds"]
            and source["creds"]["username"]
            and len(source["creds"]["username"]) > 0
        ):
            creds = "%s:%s" % (source["creds"]["username"], source["creds"]["password"])

        # Get the job list
        s_url = source["sourceURL"]
        kibble_bit.pprint("Getting job list...")
        jobsjs = jsonapi.get(
            "%s/api/json?tree=jobs[name,color]&depth=1" % s_url, auth=creds
        )

        # Get the current queue
        kibble_bit.pprint("Getting job queue...")
        queuejs = jsonapi.get("%s/queue/api/json?depth=1" % s_url, auth=creds)

        # Save queue snapshot
        NOW = int(datetime.datetime.utcnow().timestamp())
        queuehash = hashlib.sha224(
            (
                "%s-%s-queue-%s"
                % (source["organisation"], source["sourceURL"], int(time.time()))
            ).encode("ascii", errors="replace")
        ).hexdigest()

        # Scan queue items
        blocked = 0
        stuck = 0
        totalqueuetime = 0
        items = queuejs.get("items", [])

        for item in items:
            if item["blocked"]:
                blocked += 1
            if item["stuck"]:
                stuck += 1
            if "inQueueSince" in item:
                totalqueuetime += NOW - int(item["inQueueSince"] / 1000)

        avgqueuetime = totalqueuetime / max(1, len(items))

        # Count how many jobs are building, find any folders...
        actual_jobs, building = get_all_jobs(
            kibble_bit, source, jobsjs.get("jobs", []), creds
        )

        # Write up a queue doc
        queuedoc = {
            "id": queuehash,
            "date": time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(NOW)),
            "time": NOW,
            "building": building,
            "size": len(items),
            "blocked": blocked,
            "stuck": stuck,
            "avgwait": avgqueuetime,
            "ci": "jenkins",
            # Standard docs values
            "sourceID": source["sourceID"],
            "organisation": source["organisation"],
            "upsert": True,
        }
        kibble_bit.append("ci_queue", queuedoc)

        pending_jobs = actual_jobs
        kibble_bit.pprint("Found %u jobs in Jenkins" % len(pending_jobs))

        threads = []
        block = threading.Lock()
        kibble_bit.pprint("Scanning jobs using 4 sub-threads")
        for i in range(0, 4):
            t = Jenkinsthread(block, kibble_bit, source, creds, pending_jobs)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # We're all done, yaay
        kibble_bit.pprint("Done scanning %s" % source["sourceURL"])

        source["steps"]["issues"] = {
            "time": time.time(),
            "status": "Jenkins successfully scanned at "
            + time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(time.time())),
            "running": False,
            "good": True,
        }
        kibble_bit.update_source(source)


def get_all_jobs(kibble_bit, source, joblist, creds):
    real_jobs = []
    building = 0
    for job in joblist:
        # Is this a job folder?
        jclass = job.get("_class")
        if jclass in [
            "jenkins.branch.OrganizationFolder",
            "org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject",
        ]:
            kibble_bit.pprint("%s is a jobs folder, expanding..." % job["name"])
            cs_url = "%s/job/%s" % (
                source["sourceURL"],
                urllib.parse.quote(job["name"].replace("/", "%2F")),
            )
            try:
                child_jobs = jsonapi.get(
                    "%s/api/json?tree=jobs[name,color]&depth=1" % cs_url, auth=creds
                )
                csource = dict(source)
                csource["sourceURL"] = cs_url
                if not csource.get("folder"):
                    csource["folder"] = job["name"]
                else:
                    csource["folder"] += "-" + job["name"]
                cjobs, cbuilding = get_all_jobs(
                    kibble_bit, csource, child_jobs.get("jobs", []), creds
                )
                building += cbuilding
                for cjob in cjobs:
                    real_jobs.append(cjob)
            except:  # pylint: disable=bare-except
                kibble_bit.pprint("Couldn't get child jobs, bailing")
                print("%s/api/json?tree=jobs[name,color]&depth=1" % cs_url)
        # Or standard job?
        else:
            # Is it building?
            if "anime" in job.get(
                "color", ""
            ):  # a running job will have foo_anime as color
                building += 1
            job["fullURL"] = "%s/job/%s" % (
                source["sourceURL"],
                urllib.parse.quote(job["name"].replace("/", "%2F")),
            )
            job["folder"] = source.get("folder")
            real_jobs.append(job)
    return real_jobs, building

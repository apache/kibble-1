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
import os
import re
import threading
import time

from kibble.scanners.utils import jsonapi

"""
This is the Kibble Discourse scanner plugin.
"""

title = "Scanner for Discourse Forums"
version = "0.1.0"


def accepts(source):
    """ Determines whether we want to handle this source """
    if source["type"] == "discourse":
        return True
    return False


def scanJob(KibbleBit, source, cat, creds):
    """ Scans a single discourse category for activity """
    # Get $discourseURL/c/$catID
    catURL = os.path.join(source["sourceURL"], "c/%s" % cat["id"])
    KibbleBit.pprint("Scanning Discourse category '%s' at %s" % (cat["slug"], catURL))

    page = 0
    allUsers = {}

    # For each paginated result (up to page 100), check for changes
    while page < 100:
        pcatURL = "%s?page=%u" % (catURL, page)
        catjson = jsonapi.get(pcatURL, auth=creds)
        page += 1

        if catjson:

            # If we hit an empty list (no more topics), just break the loop.
            if not catjson["topic_list"]["topics"]:
                break

            # First (if we have data), we should store the known users
            # Since discourse hides the email (obviously!), we'll have to
            # fake one to generate an account.
            fakeDomain = "foo.discourse"
            m = re.match(r"https?://([-a-zA-Z0-9.]+)", source["sourceURL"])
            if m:
                fakeDomain = m.group(1)
            for user in catjson["users"]:
                # Fake email address, compute deterministic ID
                email = "%s@%s" % (user["username"], fakeDomain)
                dhash = hashlib.sha224(
                    (
                        "%s-%s-%s"
                        % (source["organisation"], source["sourceURL"], email)
                    ).encode("ascii", errors="replace")
                ).hexdigest()

                # Construct a very sparse user document
                userDoc = {
                    "id": dhash,
                    "organisation": source["organisation"],
                    "name": user["username"],
                    "email": email,
                }

                # Store user-ID-to-username mapping for later
                allUsers[user["id"]] = userDoc

                # Store it (or, queue storage) unless it exists.
                # We don't wanna override better data, so we check if
                # it's there first.
                if not KibbleBit.exists("person", dhash):
                    KibbleBit.append("person", userDoc)

            # Now, for each topic, we'll store a topic document
            for topic in catjson["topic_list"]["topics"]:

                # Calculate topic ID
                dhash = hashlib.sha224(
                    (
                        "%s-%s-topic-%s"
                        % (source["organisation"], source["sourceURL"], topic["id"])
                    ).encode("ascii", errors="replace")
                ).hexdigest()

                # Figure out when topic was created and updated
                CreatedDate = datetime.datetime.strptime(
                    topic["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
                ).timestamp()
                if topic.get("last_posted_at"):
                    UpdatedDate = datetime.datetime.strptime(
                        topic["last_posted_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
                    ).timestamp()
                else:
                    UpdatedDate = 0

                # Determine whether we should scan this topic or continue to the next one.
                # We'll do this by seeing if the topic already exists and has no changes or not.
                if KibbleBit.exists("forum_topic", dhash):
                    fdoc = KibbleBit.get("forum_topic", dhash)
                    # If update in the old doc was >= current update timestamp, skip the topic
                    if fdoc["updated"] >= UpdatedDate:
                        continue

                # Assuming we need to scan this, start by making the base topic document
                topicdoc = {
                    "id": dhash,
                    "sourceID": source["sourceID"],
                    "organisation": source["organisation"],
                    "type": "discourse",
                    "category": cat["slug"],
                    "title": topic["title"],
                    "creator": allUsers[topic["posters"][0]["user_id"]]["id"],
                    "creatorName": allUsers[topic["posters"][0]["user_id"]]["name"],
                    "created": CreatedDate,
                    "createdDate": time.strftime(
                        "%Y/%m/%d %H:%M:%S", time.gmtime(CreatedDate)
                    ),
                    "updated": UpdatedDate,
                    "solved": False,  # Discourse doesn't have this notion, but other forums might.
                    "posts": topic["posts_count"],
                    "views": topic["views"],
                    "url": source["sourceURL"]
                    + "/t/%s/%s" % (topic["slug"], topic["id"]),
                }

                KibbleBit.append("forum_topic", topicdoc)
                KibbleBit.pprint("%s is new or changed, scanning" % topicdoc["url"])

                # Now grab all the individual replies/posts
                # Remember to not have it count as a visit!
                pURL = "%s?track_visit=false&forceLoad=true" % topicdoc["url"]
                pjson = jsonapi.get(pURL, auth=creds)

                posts = pjson["post_stream"]["posts"]

                # For each post/reply, construct a forum_entry document
                KibbleBit.pprint("%s has %u posts" % (pURL, len(posts)))
                for post in posts:
                    phash = hashlib.sha224(
                        (
                            "%s-%s-post-%s"
                            % (source["organisation"], source["sourceURL"], post["id"])
                        ).encode("ascii", errors="replace")
                    ).hexdigest()
                    uname = (
                        post.get("name", post["username"]) or post["username"]
                    )  # Hack to get longest non-zero value

                    # Find the hash of the person who posted it
                    # We may know them, or we may have to store them.
                    # If we have better info now (full name), re-store
                    if (
                        post["user_id"] in allUsers
                        and allUsers[post["user_id"]]["name"] == uname
                    ):
                        uhash = allUsers[post["user_id"]]["id"]
                    else:
                        # Same as before, fake email, store...
                        email = "%s@%s" % (post["username"], fakeDomain)
                        uhash = hashlib.sha224(
                            (
                                "%s-%s-%s"
                                % (source["organisation"], source["sourceURL"], email)
                            ).encode("ascii", errors="replace")
                        ).hexdigest()

                        # Construct a very sparse user document
                        userDoc = {
                            "id": uhash,
                            "organisation": source["organisation"],
                            "name": uname,
                            "email": email,
                        }

                        # Store user-ID-to-username mapping for later
                        allUsers[user["id"]] = userDoc

                        # Store it (or, queue storage)
                        KibbleBit.append("person", userDoc)

                    # Get post date
                    CreatedDate = datetime.datetime.strptime(
                        post["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
                    ).timestamp()

                    # Store the post/reply document
                    pdoc = {
                        "id": phash,
                        "sourceID": source["sourceID"],
                        "organisation": source["organisation"],
                        "type": "discourse",
                        "creator": uhash,
                        "created": CreatedDate,
                        "createdDate": time.strftime(
                            "%Y/%m/%d %H:%M:%S", time.gmtime(CreatedDate)
                        ),
                        "topic": dhash,
                        "post_id": post["id"],
                        "text": post["cooked"],
                        "url": topicdoc["url"],
                    }
                    KibbleBit.append("forum_post", pdoc)
        else:
            KibbleBit.pprint("Fetching discourse data failed!")
            return False
    return True


class discourseThread(threading.Thread):
    """ Generic thread class for scheduling multiple scans at once """

    def __init__(self, block, KibbleBit, source, creds, jobs):
        super(discourseThread, self).__init__()
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
                self.KibbleBit.pprint(
                    "[%s] This borked, trying another one" % job["name"]
                )
                badOnes += 1
                if badOnes > 10:
                    self.KibbleBit.pprint("Too many errors, bailing!")
                    self.source["steps"]["forum"] = {
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
    discourse = re.match(r"(https?://.+)", source["sourceURL"])
    if discourse:

        source["steps"]["forum"] = {
            "time": time.time(),
            "status": "Parsing Discourse topics...",
            "running": True,
            "good": True,
        }
        KibbleBit.updateSource(source)

        pendingJobs = []
        KibbleBit.pprint("Parsing Discourse activity at %s" % source["sourceURL"])
        source["steps"]["forum"] = {
            "time": time.time(),
            "status": "Downloading changeset",
            "running": True,
            "good": True,
        }
        KibbleBit.updateSource(source)

        # Discourse may neeed credentials (if basic auth)
        creds = None
        if (
            source["creds"]
            and "username" in source["creds"]
            and source["creds"]["username"]
            and len(source["creds"]["username"]) > 0
        ):
            creds = "%s:%s" % (source["creds"]["username"], source["creds"]["password"])

        # Get the list of categories
        sURL = source["sourceURL"]
        KibbleBit.pprint("Getting categories...")
        catjs = jsonapi.get("%s/categories_and_latest" % sURL, auth=creds)

        # Directly assign the category list as pending jobs queue, ezpz.
        pendingJobs = catjs["category_list"]["categories"]

        KibbleBit.pprint("Found %u categories" % len(pendingJobs))

        # Now fire off 4 threads to parse the categories
        threads = []
        block = threading.Lock()
        KibbleBit.pprint("Scanning jobs using 4 sub-threads")
        for i in range(0, 4):
            t = discourseThread(block, KibbleBit, source, creds, pendingJobs)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # We're all done, yaay
        KibbleBit.pprint("Done scanning %s" % source["sourceURL"])

        source["steps"]["forum"] = {
            "time": time.time(),
            "status": "Discourse successfully scanned at "
            + time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(time.time())),
            "running": False,
            "good": True,
        }
        KibbleBit.updateSource(source)

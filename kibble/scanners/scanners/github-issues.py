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

import re
import hashlib
from dateutil import parser
import time
import requests

from kibble.scanners.utils import github

title = "Scanner for GitHub Issues"
version = "0.1.0"


def accepts(source):
    """ Return true if this is a github repo """
    if source["type"] == "github":
        return True
    if source["type"] == "git" and re.match(
        r"https://(?:www\.)?github.com/", source["sourceURL"]
    ):
        return True
    return False


def format_date(d, epoch=False):
    if not d:
        return
    parsed = parser.parse(d)

    if epoch:
        return time.mktime(parsed.timetuple())

    return time.strftime("%Y/%m/%d %H:%M:%S", parsed.timetuple())


def make_hash(source, issue):
    return hashlib.sha224(
        (
            "%s-%s-%s" % (source["organisation"], source["sourceID"], str(issue["id"]))
        ).encode("ascii", errors="replace")
    ).hexdigest()


def make_issue(source, issue, people):

    key = str(issue["number"])
    dhash = make_hash(source, issue)

    closed_date = issue.get("closed_at", None)

    owner_email = people[issue["user"]["login"]]["email"]

    issue_closer = owner_email
    if "closed_by" in issue:
        issue_closer = people[issue["closed_by"]["login"]]
    # Is this an issue ro a pull request?
    itype = "issue"
    if "pull_request" in issue:
        itype = "pullrequest"
    labels = []
    for l in issue.get("labels", []):
        labels.append(l["name"])
    return {
        "id": dhash,
        "key": key,
        "issuetype": itype,
        "organisation": source["organisation"],
        "sourceID": source["sourceID"],
        "url": issue["html_url"],
        "status": issue["state"],
        "labels": labels,
        "created": format_date(issue["created_at"], epoch=True),
        "closed": format_date(closed_date, epoch=True),
        "issueCloser": issue_closer,
        "createdDate": format_date(issue["created_at"]),
        "closedDate": format_date(closed_date),
        "changeDate": format_date(closed_date if closed_date else issue["updated_at"]),
        "assignee": owner_email,
        "issueCreator": owner_email,
        "comments": issue["comments"],
        "title": issue["title"],
    }


def make_person(source, issue, raw_person):
    email = raw_person["email"]
    if not email:
        email = "%s@invalid.github.com" % issue["user"]["login"]

    name = raw_person["name"]
    if not name:
        name = raw_person["login"]

    id = hashlib.sha1(
        ("%s%s" % (source["organisation"], email)).encode("ascii", errors="replace")
    ).hexdigest()

    return {
        "email": email,
        "id": id,
        "organisation": source["organisation"],
        "name": name,
    }


def status_changed(stored_issue, issue):
    return stored_issue["status"] != issue["status"]


def update_issue(KibbleBit, issue):
    KibbleBit.append("issue", issue)


def update_person(KibbleBit, person):
    person["upsert"] = True
    KibbleBit.append("person", person)


def scan(KibbleBit, source, firstAttempt=True):
    auth = None
    people = {}
    if "creds" in source:
        KibbleBit.pprint("Using auth for repo %s" % source["sourceURL"])
        creds = source["creds"]
        if creds and "username" in creds:
            auth = (creds["username"], creds["password"])
    TL = github.get_tokens_left(auth=auth)
    KibbleBit.pprint("Scanning for GitHub issues (%u tokens left on GitHub)" % TL)
    # Have we scanned before? If so, only do a 3 month scan here.
    doneBefore = False
    if source.get("steps") and source["steps"].get("issues"):
        doneBefore = True
    source["steps"]["issues"] = {
        "time": time.time(),
        "status": "Issue scan started at "
        + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()),
        "running": True,
        "good": True,
    }
    KibbleBit.updateSource(source)
    try:
        if doneBefore:
            since = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - (3 * 30 * 86400))
            )
            KibbleBit.pprint("Fetching changes since %s" % since)
            issues = github.get_all(
                source,
                github.issues,
                params={"filter": "all", "state": "all", "since": since},
                auth=auth,
            )
        else:
            issues = github.get_all(
                source,
                github.issues,
                params={"filter": "all", "state": "all"},
                auth=auth,
            )
        KibbleBit.pprint(
            "Fetched %s issues for %s" % (str(len(issues)), source["sourceURL"])
        )

        for issue in issues:

            if not issue["user"]["login"] in people:
                person = make_person(
                    source, issue, github.user(issue["user"]["url"], auth=auth)
                )
                people[issue["user"]["login"]] = person
                update_person(KibbleBit, person)

            if "closed_by" in issue and not issue["closed_by"]["login"] in people:
                closer = make_person(
                    source, issue, github.user(issue["closed_by"]["url"], auth=auth)
                )
                people[issue["closed_by"]["login"]] = closer
                update_person(KibbleBit, closer)

            doc = make_issue(source, issue, people)
            dhash = doc["id"]
            stored_change = None
            if KibbleBit.exists("issue", dhash):
                es_doc = KibbleBit.get("issue", dhash)
                if not status_changed(es_doc, doc):
                    # KibbleBit.pprint("change %s seen already and status unchanged. Skipping." % issue['id'])
                    continue

            update_issue(KibbleBit, doc)

        source["steps"]["issues"] = {
            "time": time.time(),
            "status": "Issue scan completed at "
            + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()),
            "running": False,
            "good": True,
        }
        KibbleBit.updateSource(source)

    except requests.HTTPError as e:
        # If we errored out because of rate limiting, retry later, otherwise bail
        if firstAttempt:
            sleeps = 0
            if github.get_tokens_left(auth=auth) < 10:
                KibbleBit.pprint("Hit rate limits, trying to sleep it off!")
                while github.get_tokens_left(auth=auth) < 10:
                    sleeps += 1
                    if sleeps > 24:
                        KibbleBit.pprint(
                            "Slept for too long without finding a reset rate limit, giving up!"
                        )
                        break
                    time.sleep(300)  # Sleep 5 min, then check again..
                # If we have tokens, try one more time...
                if github.get_tokens_left(auth=auth) > 10:
                    scan(KibbleBit, source, False)  # If this one fails, bail completely
                    return

        KibbleBit.pprint("HTTP Error, rate limit exceeded?")
        source["steps"]["issues"] = {
            "time": time.time(),
            "status": "Issue scan failed at "
            + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
            + ": "
            + e.response.text,
            "running": False,
            "good": False,
        }
        KibbleBit.updateSource(source)

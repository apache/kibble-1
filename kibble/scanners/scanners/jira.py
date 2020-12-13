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

import hashlib
import re
import threading
import time

import requests.exceptions

from kibble.scanners.utils import jsonapi

"""
This is the Kibble JIRA scanner plugin.
"""

title = "Scanner for Atlassian JIRA"
version = "0.1.0"


def accepts(source):
    """ Determines whether we want to handle this source """
    if source["type"] == "jira":
        return True
    if source["type"] == "issuetracker":
        jira = re.match(r"(https?://.+)/browse/([A-Z0-9]+)", url)
        if jira:
            return True
    return False


def getTime(string):
    return time.mktime(
        time.strptime(re.sub(r"\..*", "", str(string)), "%Y-%m-%dT%H:%M:%S")
    )


def assigned(js):
    if "items" in js:
        for item in js["items"]:
            if item["field"] == "assignee":
                return True
    return False


def wfi(js):
    if "items" in js:
        for item in js["items"]:
            if item["field"] == "status" and item["toString"] == "Waiting for Infra":
                return True
    return False


def wfu(js):
    if "items" in js:
        for item in js["items"]:
            if item["field"] == "status" and item["toString"] == "Waiting for user":
                return True
    return False


def moved(js):
    if "items" in js:
        for item in js["items"]:
            if item["field"] == "Key" and item["toString"].find("INFRA-") != -1:
                return True
    return False


def wasclosed(js):
    if "changelog" in js:
        cjs = js["changelog"]["histories"]
        for citem in cjs:
            if "items" in citem:
                for item in citem["items"]:
                    if item["field"] == "status" and (
                        item["toString"].lower().find("closed") != -1
                        or item["toString"].lower().find("resolved") != -1
                    ):
                        return True, citem.get("author", {})
    else:
        if "items" in js:
            for item in js["items"]:
                if item["field"] == "status" and (
                    item["toString"].find("Closed") != -1
                ):
                    return True, None
    return False, None


def resolved(js):
    if "items" in js:
        for item in js["items"]:
            if item["field"] == "resolution" and (
                item["toString"] != "Pending Closed"
                and item["toString"] != "Unresolved"
            ):
                return True
    return False


def pchange(js):
    if "items" in js:
        for item in js["items"]:
            if item["field"] == "priority":
                return True
    return False


def scanTicket(KibbleBit, key, u, source, creds, openTickets):
    """ Scans a single ticket for activity and people """

    dhash = hashlib.sha224(
        ("%s-%s-%s" % (source["organisation"], source["sourceURL"], key)).encode(
            "ascii", errors="replace"
        )
    ).hexdigest()
    found = True
    parseIt = False

    # the 'domain' var we try to figure out here is used
    # for faking email addresses and keep them unique,
    # in case JIRA has email visibility turned off.
    domain = "jira"
    m = re.search(r"https?://([^/]+)", u)
    if m:
        domain = m.group(1)

    found = KibbleBit.exists("issue", dhash)
    if not found:
        KibbleBit.pprint("[%s] We've never seen this ticket before, parsing..." % key)
        parseIt = True
    else:
        ticket = KibbleBit.get("issue", dhash)
        if ticket["status"] == "closed" and key in openTickets:
            KibbleBit.pprint("[%s] Ticket was reopened, reparsing" % key)
            parseIt = True
        elif ticket["status"] == "open" and not key in openTickets:
            KibbleBit.pprint("[%s] Ticket was recently closed, parsing it" % key)
            parseIt = True
        else:
            if (
                ticket["issueCreator"] == "unknown@kibble"
                or ticket["issueCloser"] == "unknown@kibble"
            ):  # Gotta redo these!
                parseIt = True
                KibbleBit.pprint(
                    "[%s] Ticket contains erroneous data from a previous scan, reparsing"
                    % key
                )
            # This is just noise!
            # KibbleBit.pprint("[%s] Ticket hasn't changed, ignoring..." % key)

    if parseIt:
        KibbleBit.pprint("[%s] Parsing data from JIRA at %s..." % (key, domain))
        queryURL = (
            "%s/rest/api/2/issue/%s?fields=creator,reporter,status,issuetype,summary,assignee,resolutiondate,created,priority,changelog,comment,resolution,votes&expand=changelog"
            % (u, key)
        )
        jiraURL = "%s/browse/%s" % (u, key)
        try:
            tjson = jsonapi.get(queryURL, auth=creds)
            if not tjson:
                KibbleBit.pprint("%s does not exist (404'ed)" % key)
                return False
        except requests.exceptions.ConnectionError as err:
            KibbleBit.pprint(f"Connection error: {err}, skipping this ticket for now!")
            return False
        st, closer = wasclosed(tjson)
        if st and not closer:
            KibbleBit.pprint("Closed but no closer??")
        closerEmail = None
        status = "closed" if st else "open"

        # Make sure we actually have field data to work with
        if not tjson.get("fields") or not tjson["fields"].get("created"):
            KibbleBit.pprint(
                "[%s] JIRA response is missing field data, ignoring ticket." % key
            )
            return False

        cd = getTime(tjson["fields"]["created"])
        rd = (
            getTime(tjson["fields"]["resolutiondate"])
            if "resolutiondate" in tjson["fields"] and tjson["fields"]["resolutiondate"]
            else None
        )
        comments = 0
        if "comment" in tjson["fields"] and tjson["fields"]["comment"]:
            comments = tjson["fields"]["comment"]["total"]
        assignee = (
            tjson["fields"]["assignee"].get(
                "emailAddress",  # Try email, fall back to username
                tjson["fields"]["assignee"].get("name"),
            )
            if tjson["fields"].get("assignee")
            else None
        )
        creator = (
            tjson["fields"]["reporter"].get(
                "emailAddress",  # Try email, fall back to username
                tjson["fields"]["reporter"].get("name"),
            )
            if tjson["fields"].get("reporter")
            else None
        )
        title = tjson["fields"]["summary"]
        if closer:
            # print("Parsing closer")
            closerEmail = (
                closer.get("emailAddress", closer.get("name"))
                .replace(" dot ", ".", 10)
                .replace(" at ", "@", 1)
            )
            if not "@" in closerEmail:
                closerEmail = "%s@%s" % (closerEmail, domain)
            displayName = closer.get("displayName", "Unkown")
            if displayName and len(displayName) > 0:
                # Add to people db
                pid = hashlib.sha1(
                    ("%s%s" % (source["organisation"], closerEmail)).encode(
                        "ascii", errors="replace"
                    )
                ).hexdigest()
                jsp = {
                    "name": displayName,
                    "email": closerEmail,
                    "organisation": source["organisation"],
                    "id": pid,
                    "upsert": True,
                }
                KibbleBit.append("person", jsp)

        if creator:
            creator = creator.replace(" dot ", ".", 10).replace(" at ", "@", 1)
            if not "@" in creator:
                creator = "%s@%s" % (creator, domain)
            displayName = (
                tjson["fields"]["reporter"]["displayName"]
                if tjson["fields"]["reporter"]
                else None
            )
            if displayName and len(displayName) > 0:
                # Add to people db
                pid = hashlib.sha1(
                    ("%s%s" % (source["organisation"], creator)).encode(
                        "ascii", errors="replace"
                    )
                ).hexdigest()
                jsp = {
                    "name": displayName,
                    "email": creator,
                    "organisation": source["organisation"],
                    "id": pid,
                    "upsert": True,
                }
                KibbleBit.append("person", jsp)
        if assignee and not "@" in assignee:
            assignee = "%s@%s" % (assignee, domain)
        jso = {
            "id": dhash,
            "key": key,
            "organisation": source["organisation"],
            "sourceID": source["sourceID"],
            "url": jiraURL,
            "status": status,
            "created": cd,
            "closed": rd,
            "issuetype": "issue",
            "issueCloser": closerEmail,
            "createdDate": time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(cd)),
            "closedDate": time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(rd))
            if rd
            else None,
            "changeDate": time.strftime(
                "%Y/%m/%d %H:%M:%S", time.gmtime(rd if rd else cd)
            ),
            "assignee": assignee,
            "issueCreator": creator,
            "comments": comments,
            "title": title,
        }
        KibbleBit.append("issue", jso)
    return True


#
# except Exception as err:
# KibbleBit.pprint(err)
# return False


class jiraThread(threading.Thread):
    def __init__(self, block, KibbleBit, source, creds, pt, ot):
        super(jiraThread, self).__init__()
        self.block = block
        self.KibbleBit = KibbleBit
        self.creds = creds
        self.source = source
        self.pendingTickets = pt
        self.openTickets = ot

    def run(self):
        badOnes = 0
        while len(self.pendingTickets) > 0 and badOnes <= 50:
            # print("%u elements left to count" % len(pendingTickets))
            self.block.acquire()
            try:
                rl = self.pendingTickets.pop(0)
            except Exception as err:
                print(f"An error occured: {err}")
                self.block.release()
                return
            if not rl:
                self.block.release()
                return
            self.block.release()
            if not scanTicket(
                self.KibbleBit, rl[0], rl[1], rl[2], self.creds, self.openTickets
            ):
                self.KibbleBit.pprint("[%s] This borked, trying another one" % rl[0])
                badOnes += 1
                if badOnes > 100:
                    self.KibbleBit.pprint("Too many errors, bailing!")
                    self.source["steps"]["issues"] = {
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
    jira = re.match(r"(https?://.+)/browse/([A-Z0-9]+)", source["sourceURL"])
    if jira:

        # JIRA NEEDS credentials to do a proper scan!
        creds = None
        if (
            source["creds"]
            and "username" in source["creds"]
            and source["creds"]["username"]
            and len(source["creds"]["username"]) > 0
        ):
            creds = "%s:%s" % (source["creds"]["username"], source["creds"]["password"])
        if not creds:
            KibbleBit.pprint(
                "JIRA at %s requires authentication, but none was found! Bailing."
                % source["sourceURL"]
            )
            source["steps"]["issues"] = {
                "time": time.time(),
                "status": "Parsing JIRA changes...",
                "running": True,
                "good": True,
            }
            KibbleBit.updateSource(source)
            return

        source["steps"]["issues"] = {
            "time": time.time(),
            "status": "Parsing JIRA changes...",
            "running": True,
            "good": True,
        }
        KibbleBit.updateSource(source)

        pendingTickets = []
        KibbleBit.pprint("Parsing JIRA activity at %s" % source["sourceURL"])
        source["steps"]["issues"] = {
            "time": time.time(),
            "status": "Downloading changeset",
            "running": True,
            "good": True,
        }
        KibbleBit.updateSource(source)

        # Get base URL, list and domain to parse
        u = jira.group(1)
        instance = jira.group(2)
        lastTicket = 0
        latestURL = (
            "%s/rest/api/2/search?jql=project=%s+order+by+createdDate+DESC&fields=id,key&maxResults=1"
            % (u, instance)
        )
        js = None

        js = jsonapi.get(latestURL, auth=creds)
        if "issues" in js and len(js["issues"]) == 1:
            key = js["issues"][0]["key"]
            m = re.search(r"-(\d+)$", key)
            if m:
                lastTicket = int(m.group(1))

        openTickets = []
        startAt = 0
        badTries = 0
        while True and badTries < 10:
            openURL = (
                "%s/rest/api/2/search?jql=project=%s+and+status=open+order+by+createdDate+ASC&fields=id,key&maxResults=100&startAt=%u"
                % (u, instance, startAt)
            )
            # print(openURL)
            try:
                ojs = jsonapi.get(openURL, auth=creds)
                if not "issues" in ojs or len(ojs["issues"]) == 0:
                    break
                for item in ojs["issues"]:
                    openTickets.append(item["key"])
                KibbleBit.pprint("Found %u open tickets" % len(openTickets))
                startAt += 100
            except:
                KibbleBit.pprint("JIRA borked, retrying")
                badTries += 1
        KibbleBit.pprint("Found %u open tickets" % len(openTickets))

        badOnes = 0
        for i in reversed(range(1, lastTicket + 1)):
            key = "%s-%u" % (instance, i)
            pendingTickets.append([key, u, source])

        threads = []
        block = threading.Lock()
        KibbleBit.pprint("Scanning tickets using 4 sub-threads")
        for i in range(0, 4):
            t = jiraThread(block, KibbleBit, source, creds, pendingTickets, openTickets)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        KibbleBit.pprint("Done scanning %s" % source["sourceURL"])

        source["steps"]["issues"] = {
            "time": time.time(),
            "status": "Issue tracker (JIRA) successfully scanned at "
            + time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(time.time())),
            "running": False,
            "good": True,
        }
        KibbleBit.updateSource(source)

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

""" This is the BugZilla scanner plugin for Kibble """

import hashlib
import json
import re
import time
import urllib
from threading import Lock, Thread

from kibble.scanners.utils import jsonapi

title = "Scanner for BugZilla"
version = "0.1.0"


def accepts(source):
    """ Determine if this is a BugZilla source """
    if source["type"] == "bugzilla":
        return True
    if source["type"] == "issuetracker":
        bz = re.match(
            r"(https?://\S+?)(/jsonrpc\.cgi)?[\s:?]+(.+)", source["sourceURL"]
        )
        if bz:
            return True
    return False


def get_time(string):
    return time.mktime(
        time.strptime(re.sub(r"[zZ]", "", str(string)), "%Y-%m-%dT%H:%M:%S")
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


def was_closed(js):
    if "changelog" in js:
        cjs = js["changelog"]["histories"]
        for citem in cjs:
            if "items" in citem:
                for item in citem["items"]:
                    if item["field"] == "status" and (
                        item["toString"] == "Closed" or item["toString"] == "Resolved"
                    ):
                        return True, citem["author"]
    else:
        if "items" in js:
            for item in js["items"]:
                if item["field"] == "status" and item["toString"] == "Closed":
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


def scan_ticket(bug, kibble_bit, source, open_tickets, u, dom):
    try:
        key = bug["id"]
        dhash = hashlib.sha224(
            ("%s-%s-%s" % (source["organisation"], source["sourceURL"], key)).encode(
                "ascii", errors="replace"
            )
        ).hexdigest()
        found = kibble_bit.exists("issue", dhash)
        parseIt = False
        if not found:
            parseIt = True
        else:
            ticket = kibble_bit.get("issue", dhash)
            if ticket["status"] == "closed" and key in open_tickets:
                kibble_bit.pprint("Ticket was reopened, reparsing")
                parseIt = True
            elif ticket["status"] == "open" and not key in open_tickets:
                kibble_bit.pprint("Ticket was recently closed, parsing it")
                parseIt = True
            else:
                pass
                # print("Ticket hasn't changed, ignoring...")

        if parseIt:
            kibble_bit.pprint("Parsing data from BugZilla for #%s" % key)

            params = {"ids": [int(key)], "limit": 0}
            if (
                source["creds"]
                and "username" in source["creds"]
                and source["creds"]["username"]
                and len(source["creds"]["username"]) > 0
            ):
                params["Bugzilla_login"] = source["creds"]["username"]
                params["Bugzilla_password"] = source["creds"]["password"]
            ticketsURL = "%s?method=Bug.get&params=[%s]" % (
                u,
                urllib.parse.quote(json.dumps(params)),
            )

            js = jsonapi.get(ticketsURL)
            js = js["result"]["bugs"][0]
            creator = {"name": bug["creator"], "email": js["creator"]}
            closer = {}
            cd = get_time(js["creation_time"])
            rd = None
            status = "open"
            if js["status"] in ["CLOSED", "RESOLVED"]:
                status = "closed"
                kibble_bit.pprint("%s was closed, finding out who did that" % key)
                ticketsURL = "%s?method=Bug.history&params=[%s]" % (
                    u,
                    urllib.parse.quote(json.dumps(params)),
                )
                hjs = jsonapi.get(ticketsURL)
                history = hjs["result"]["bugs"][0]["history"]
                for item in history:
                    for change in item["changes"]:
                        if (
                            change["field_name"] == "status"
                            and "added" in change
                            and change["added"] in ["CLOSED", "RESOLVED"]
                        ):
                            rd = get_time(item["when"])
                            closer = {"name": item["who"], "email": item["who"]}
                            break
            kibble_bit.pprint("Counting comments for %s..." % key)
            ticketsURL = "%s?method=Bug.comments&params=[%s]" % (
                u,
                urllib.parse.quote(json.dumps(params)),
            )
            hjs = jsonapi.get(ticketsURL)
            comments = len(hjs["result"]["bugs"][str(key)]["comments"])

            title = bug["summary"]
            del params["ids"]
            if closer:

                pid = hashlib.sha1(
                    ("%s%s" % (source["organisation"], closer["email"])).encode(
                        "ascii", errors="replace"
                    )
                ).hexdigest()
                found = kibble_bit.exists("person", pid)
                if not found:
                    params["names"] = [closer["email"]]
                    ticketsURL = "%s?method=User.get&params=[%s]" % (
                        u,
                        urllib.parse.quote(json.dumps(params)),
                    )

                    try:
                        ujs = jsonapi.get(ticketsURL)
                        displayName = ujs["result"]["users"][0]["real_name"]
                    except:  # pylint: disable=bare-except  # pylint: disable=bare-except
                        displayName = closer["email"]
                    if displayName and len(displayName) > 0:
                        # Add to people db

                        jsp = {
                            "name": displayName,
                            "email": closer["email"],
                            "organisation": source["organisation"],
                            "id": pid,
                        }
                        # print("Updating person DB for closer: %s (%s)" % (displayName, closerEmail))
                        kibble_bit.index("person", pid, jsp)

            if creator:
                pid = hashlib.sha1(
                    ("%s%s" % (source["organisation"], creator["email"])).encode(
                        "ascii", errors="replace"
                    )
                ).hexdigest()
                found = kibble_bit.exists("person", pid)
                if not found:
                    if not creator["name"]:
                        params["names"] = [creator["email"]]
                        ticketsURL = "%s?method=User.get&params=[%s]" % (
                            u,
                            urllib.parse.quote(json.dumps(params)),
                        )
                        try:
                            ujs = jsonapi.get(ticketsURL)
                            creator["name"] = ujs["result"]["users"][0]["real_name"]
                        except:  # pylint: disable=bare-except  # pylint: disable=bare-except
                            creator["name"] = creator["email"]
                    if creator["name"] and len(creator["name"]) > 0:
                        # Add to people db

                        jsp = {
                            "name": creator["name"],
                            "email": creator["email"],
                            "organisation": source["organisation"],
                            "id": pid,
                        }
                        kibble_bit.index("person", pid, jsp)

            jso = {
                "id": dhash,
                "key": key,
                "organisation": source["organisation"],
                "sourceID": source["sourceID"],
                "url": "%s/show_bug.cgi?id=%s" % (dom, key),
                "status": status,
                "created": cd,
                "closed": rd,
                "issuetype": "issue",
                "issueCloser": closer["email"] if "email" in closer else None,
                "createdDate": time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(cd)),
                "closedDate": time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(rd))
                if rd
                else None,
                "changeDate": time.strftime(
                    "%Y/%m/%d %H:%M:%S", time.gmtime(rd if rd else cd)
                ),
                "assignee": None,
                "issueCreator": creator["email"],
                "comments": comments,
                "title": title,
            }
            kibble_bit.append("issue", jso)
            time.sleep(0.5)  # BugZilla is notoriously slow. Maybe remove this later
        return True
    except Exception as err:
        kibble_bit.pprint(err)
        return False


class BzThread(Thread):
    def __init__(self, KibbleBit, source, block, pt, ot, u, dom):
        super().__init__()
        self.KibbleBit = KibbleBit
        self.source = source
        self.block = block
        self.pendingTickets = pt
        self.openTickets = ot
        self.u = u
        self.dom = dom

    def run(self):
        bad_ones = 0

        while len(self.pendingTickets) > 0 and bad_ones <= 50:
            if len(self.pendingTickets) % 10 == 0:
                self.KibbleBit.pprint(
                    "%u elements left to count" % len(self.pendingTickets)
                )
            self.block.acquire()
            try:
                rl = self.pendingTickets.pop(0)
            except Exception:  # list empty, likely
                self.block.release()
                return
            if not rl:
                self.block.release()
                return
            self.block.release()
            if not scan_ticket(
                rl, self.KibbleBit, self.source, self.openTickets, self.u, self.dom
            ):
                self.KibbleBit.pprint("Ticket %s seems broken, skipping" % rl["id"])
                bad_ones += 1
                if bad_ones > 50:
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
    url = source["sourceURL"]

    source["steps"]["issues"] = {
        "time": time.time(),
        "status": "Parsing BugZilla changes...",
        "running": True,
        "good": True,
    }
    kibble_bit.update_source(source)

    bz = re.match(r"(https?://\S+?)(/jsonrpc\.cgi)?[\s:?]+(.+)", url)
    if bz:
        if (
            source["creds"]
            and "username" in source["creds"]
            and source["creds"]["username"]
            and len(source["creds"]["username"]) > 0
        ):
            creds = "%s:%s" % (source["creds"]["username"], source["creds"]["password"])
        pending_tickets = []
        open_tickets = []

        # Get base URL, list and domain to parse
        dom = bz.group(1)
        dom = re.sub(r"/+$", "", dom)
        u = "%s/jsonrpc.cgi" % dom
        instance = bz.group(3)

        params = {
            "product": [instance],
            "status": [
                "RESOLVED",
                "CLOSED",
                "NEW",
                "UNCOMFIRMED",
                "ASSIGNED",
                "REOPENED",
                "VERIFIED",
            ],
            "include_fields": ["id", "creation_time", "status", "summary", "creator"],
            "limit": 10000,
            "offset": 1,
        }
        # If * is requested, just omit the product name
        if instance == "*":
            params = {
                "status": [
                    "RESOLVED",
                    "CLOSED",
                    "NEW",
                    "UNCOMFIRMED",
                    "ASSIGNED",
                    "REOPENED",
                    "VERIFIED",
                ],
                "include_fields": [
                    "id",
                    "creation_time",
                    "status",
                    "summary",
                    "creator",
                ],
                "limit": 10000,
                "offset": 1,
            }

        tickets_url = "%s?method=Bug.search&params=[%s]" % (
            u,
            urllib.parse.quote(json.dumps(params)),
        )

        while True:
            try:
                js = jsonapi.get(tickets_url, auth=creds)
            except:  # pylint: disable=bare-except  # pylint: disable=bare-except
                kibble_bit.pprint("Couldn't fetch more tickets, bailing")
                break

            if len(js["result"]["bugs"]) > 0:
                kibble_bit.pprint(
                    "%s: Found %u tickets..."
                    % (
                        source["sourceURL"],
                        ((params.get("offset", 1) - 1) + len(js["result"]["bugs"])),
                    )
                )
                for bug in js["result"]["bugs"]:
                    pending_tickets.append(bug)
                    if bug["status"] not in ["RESOLVED", "CLOSED"]:
                        open_tickets.append(bug["id"])
                params["offset"] += 10000
                tickets_url = "%s?method=Bug.search&params=[%s]" % (
                    u,
                    urllib.parse.quote(json.dumps(params)),
                )
            else:
                kibble_bit.pprint("No more tickets left to scan")
                break

        kibble_bit.pprint(
            "Found %u open tickets, %u closed."
            % (len(open_tickets), len(pending_tickets) - len(open_tickets))
        )

        block = Lock()
        threads = []
        # TODO: Fix this loop
        for i in range(0, 4):
            t = BzThread(
                kibble_bit, source, block, pending_tickets, open_tickets, u, dom
            )
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        source["steps"]["issues"] = {
            "time": time.time(),
            "status": "Issue tracker (BugZilla) successfully scanned at "
            + time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(time.time())),
            "running": False,
            "good": True,
        }
        kibble_bit.update_source(source)

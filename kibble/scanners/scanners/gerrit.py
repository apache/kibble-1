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
import json
import re
import time

import requests
from dateutil import parser

title = "Scanner for Gerrit Code Review"
version = "0.1.1"


CHANGES_URL = "%s/changes/%s"
PROJECT_LIST_URL = "%s/projects/"
ACCOUNTS_URL = "%s/accounts/%d"
COMMIT_ID_RE = re.compile("    Change-Id: (.*)")


def accepts(source):
    """ Do we accept this source?? """
    if source["type"] == "gerrit":
        return True
    return False


def getjson(response):
    response.raise_for_status()
    return json.loads(response.text[4:])


def get(url, params=None):
    resp = requests.get(url, params=params)
    return getjson(resp)


def changes(base_url, params=None):
    return get(CHANGES_URL % (base_url, ""), params=params)


def change_details(base_url, change):
    if isinstance(change, dict):
        id = change["change_id"]
    else:
        id = change

    return get(CHANGES_URL % (base_url, id) + "/detail")


def get_commit_id(commit_message):
    all = COMMIT_ID_RE.findall(commit_message)
    if all:
        return all[0]
    return None


def get_all(base_url, f, params=None):
    if params is None:
        params = {}
    acc = []

    while True:
        items = f(base_url, params=params)
        if not items:
            break

        acc.extend(items)
        params.update({"start": len(acc)})

    return acc


def format_date(d, epoch=False):
    if not d:
        return
    parsed = parser.parse(d)

    if epoch:
        return time.mktime(parsed.timetuple())

    return time.strftime("%Y/%m/%d %H:%M:%S", parsed.timetuple())


def make_hash(repo, change):
    return hashlib.sha224(
        (
            "%s-%s-%s" % (repo["organisation"], repo["sourceID"], change["change_id"])
        ).encode("ascii", errors="replace")
    ).hexdigest()


def is_closed(change):
    return change["status"] == "MERGED" or change["status"] == "ABANDONED"


def make_issue(repo, base_url, change):
    key = change["change_id"]
    dhash = make_hash(repo, change)

    closed_date = None
    if is_closed(change):
        closed_date = change["updated"]

    if "email" not in change["owner"]:
        change["owner"]["email"] = "%u@invalid.gerrit" % change["owner"]["_account_id"]
    owner_email = change["owner"]["email"]

    messages = []
    for message in change.get("messages", []):
        messages.append(message.get("message", ""))

    return {
        "id": dhash,
        "key": key,
        "organisation": repo["organisation"],
        "sourceID": repo["sourceID"],
        "url": base_url + "/#/q/" + key,
        "status": change["status"],
        "created": format_date(change["created"], epoch=True),
        "closed": format_date(closed_date, epoch=True),
        "issueCloser": owner_email,
        "createdDate": format_date(change["created"]),
        "closedDate": format_date(closed_date),
        "changeDate": format_date(closed_date if closed_date else change["created"]),
        "assignee": owner_email,
        "issueCreator": owner_email,
        "comments": len(messages),
        "title": change["subject"],
    }


def make_person(repo, raw_person):
    email = raw_person["email"]
    id = hashlib.sha1(
        ("%s%s" % (repo["organisation"], email)).encode("ascii", errors="replace")
    ).hexdigest()
    return {
        "email": email,
        "id": id,
        "organisation": repo["organisation"],
        "name": raw_person["name"]
        if "name" in raw_person
        else "%u" % raw_person["_account_id"],
    }


def update_issue(kibble_bit, issue):
    id = issue["id"]
    kibble_bit.pprint("Updating issue: " + id)
    kibble_bit.index("issue", id, issue)


def update_person(kibble_bit, person):
    kibble_bit.pprint("Updating person: " + person["name"] + " - " + person["email"])
    kibble_bit.index("person", person["id"], {"doc": person, "doc_as_upsert": True})


def status_changed(stored_change, change):
    if not stored_change or not change:
        return True
    return stored_change["status"] != change["status"]


def scan(kibble_bit, source):
    source["steps"]["issues"] = {
        "time": time.time(),
        "status": "Analyzing Gerrit tickets...",
        "running": True,
        "good": True,
    }
    kibble_bit.update_source(source)

    url = source["sourceURL"]
    # Try matching foo.bar/r/project/subfoo
    m = re.match(r"(.+://.+?/r)/(.+)", url)
    if m:
        base_url = m.group(1)
        project_name = m.group(2)
    # Fall back to old splitty split
    else:
        url = re.sub(r"^git://", "http://", url)
        source_parts = url.split("/")
        project_name = source_parts[-1]
        base_url = "/".join(source_parts[:-1])  # remove the trailing /blah/

    # TODO: figure out branch from current checkout
    q = (
        '(is:open OR is:new OR is:closed OR is:merged OR is:abandoned) AND project:"%s"'
        % project_name
    )
    all_changes = get_all(
        base_url, changes, {"q": q, "o": ["LABELS", "DETAILED_ACCOUNTS"]}
    )

    print("Found " + str(len(all_changes)) + " changes for project: " + project_name)

    people = {}
    for change in all_changes:
        try:
            # TODO: check if needs updating here before getting details
            dhash = make_hash(source, change)

            stored_change = None
            if kibble_bit.exists("issue", dhash):
                stored_change = kibble_bit.get("issue", dhash)

            if not status_changed(stored_change, change):
                # print("change %s seen already and status unchanged. Skipping." %
                #      change['change_id'])
                continue

            details = change_details(base_url, change)

            issue_doc = make_issue(source, base_url, details)
            update_issue(kibble_bit, issue_doc)

            labels = details["labels"]
            change_people = []

            if "owner" in details:
                change_people.append(details["owner"])
            if "Module-Owner" in labels and "all" in labels["Module-Owner"]:
                change_people.extend(labels["Module-Owner"]["all"])
            if "Code-Review" in labels and "all" in labels["Code-Review"]:
                change_people.extend(labels["Code-Review"]["all"])
            if "Verified" in labels and "all" in labels["Verified"]:
                change_people.extend(labels["Verified"]["all"])

            print(change["change_id"] + " -> " + str(len(change_people)) + " people.")

            for person in change_people:
                if "email" in person and person["email"] not in people:
                    people[person["email"]] = person
                    update_person(kibble_bit, make_person(source, person))

        except requests.HTTPError as e:
            print(e)

    source["steps"]["issues"] = {
        "time": time.time(),
        "status": "Done analyzing tickets!",
        "running": False,
        "good": True,
    }
    kibble_bit.update_source(source)

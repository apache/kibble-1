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
import time

from kibble.scanners.utils import github

title = "Traffic statistics plugin for GitHub repositories"
version = "0.1.0"


def accepts(source):
    """ Do we accept this source? """
    if source["type"] == "github":
        return True
    return False


def get_time(string):
    """ Convert GitHub timestamp to epoch """
    return time.mktime(
        time.strptime(re.sub(r"Z", "", str(string)), "%Y-%m-%dT%H:%M:%S")
    )


def scan(kibble_bit, source):

    # Get some vars, construct a data path for the repo
    url = source["sourceURL"]

    auth = None
    if "creds" in source:
        kibble_bit.pprint("Using auth for repo %s" % source["sourceURL"])
        creds = source["creds"]
        if creds and "username" in creds:
            auth = (creds["username"], creds["password"])
    else:
        kibble_bit.pprint(
            "GitHub stats requires auth, none provided. Ignoring this repo."
        )
        return
    try:
        source["steps"]["stats"] = {
            "time": time.time(),
            "status": "Fetching statistics from source location...",
            "running": True,
            "good": True,
        }
        kibble_bit.update_source(source)

        # Get views
        views = github.views(url, auth)
        if "views" in views:
            for el in views["views"]:
                ts = get_time(el["timestamp"])
                shash = hashlib.sha224(
                    (
                        "%s-%s-%s-clones"
                        % (source["organisation"], url, el["timestamp"])
                    ).encode("ascii", errors="replace")
                ).hexdigest()
                bit = {
                    "organisation": source["organisation"],
                    "sourceURL": source["sourceURL"],
                    "sourceID": source["sourceID"],
                    "date": time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(ts)),
                    "count": el["count"],
                    "uniques": el["uniques"],
                    "ghtype": "views",
                    "id": shash,
                }
                kibble_bit.append("ghstats", bit)

        # Get clones
        clones = github.clones(url, auth)
        if "clones" in clones:
            for el in clones["clones"]:
                ts = get_time(el["timestamp"])
                shash = hashlib.sha224(
                    (
                        "%s-%s-%s-clones"
                        % (source["organisation"], url, el["timestamp"])
                    ).encode("ascii", errors="replace")
                ).hexdigest()
                bit = {
                    "organisation": source["organisation"],
                    "sourceURL": source["sourceURL"],
                    "sourceID": source["sourceID"],
                    "date": time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(ts)),
                    "count": el["count"],
                    "uniques": el["uniques"],
                    "ghtype": "clones",
                    "id": shash,
                }
                kibble_bit.append("ghstats", bit)

        # Get referrers
        refs = github.referrers(url, auth)
        if refs:
            for el in refs:
                el["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.time())
                ts = get_time(el["timestamp"])
                shash = hashlib.sha224(
                    (
                        "%s-%s-%s-refs" % (source["organisation"], url, el["timestamp"])
                    ).encode("ascii", errors="replace")
                ).hexdigest()
                bit = {
                    "organisation": source["organisation"],
                    "sourceURL": source["sourceURL"],
                    "sourceID": source["sourceID"],
                    "date": time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(ts)),
                    "count": el["count"],
                    "uniques": el["uniques"],
                    "ghtype": "referrers",
                    "id": shash,
                }
                kibble_bit.append("ghstats", bit)
    except:  # pylint: disable=bare-except
        pass
        # All done!

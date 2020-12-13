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

import os
import subprocess
import time

from kibble.scanners.utils import git, sloc

""" Source Lines of Code counter for Git """

title = "SloC Counter for Git"
version = "0.1.0"


def accepts(source):
    """ Do we accept this source? """
    if source["type"] == "git":
        return True
    # There are cases where we have a github repo, but don't wanna analyze the code, just issues
    if source["type"] == "github" and source.get("issuesonly", False) == False:
        return True
    return False


def scan(KibbleBit, source):

    rid = source["sourceID"]
    url = source["sourceURL"]
    rootpath = "%s/%s/git" % (
        KibbleBit.config["scanner"]["scratchdir"],
        source["organisation"],
    )
    gpath = os.path.join(rootpath, rid)

    if source["steps"]["sync"]["good"] and os.path.exists(gpath):
        source["steps"]["count"] = {
            "time": time.time(),
            "status": "SLoC count started at "
            + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()),
            "running": True,
            "good": True,
        }
        KibbleBit.updateSource(source)

        try:
            branch = git.defaultBranch(source, gpath)
            subprocess.call("cd %s && git checkout %s" % (gpath, branch), shell=True)
        except:
            KibbleBit.pprint("SLoC counter failed to find main branch for %s!!" % url)
            return False

        KibbleBit.pprint("Running SLoC count for %s" % url)
        languages, codecount, comment, blank, years, cost = sloc.count(gpath)

        sloc_ = {
            "sourceID": source["sourceID"],
            "loc": codecount,
            "comments": comment,
            "blanks": blank,
            "years": years,
            "cost": cost,
            "languages": languages,
        }
        source["sloc"] = sloc_
        source["steps"]["count"] = {
            "time": time.time(),
            "status": "SLoC count completed at "
            + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()),
            "running": False,
            "good": True,
        }
        KibbleBit.updateSource(source)

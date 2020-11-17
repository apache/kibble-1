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

""" This is the Kibble git utility plugin """

import os
import re
import subprocess
import sys


def defaultBranch(source, datapath, KibbleBit=None):
    """ Tries to figure out what the main branch of a repo is """
    wanted_branches = ["master", "main", "trunk"]
    branch = ""
    # If we have an override of branches we like, use 'em
    if KibbleBit and KibbleBit.config.get("git"):
        wanted_branches = KibbleBit.config["git"].get(
            "wanted_branches", wanted_branches
        )
    foundBranch = False

    # For each wanted branch, in order, look for it in our clone,
    # and return the name if found.
    for B in wanted_branches:
        try:
            branch = (
                subprocess.check_output(
                    "cd %s && git rev-parse --abbrev-ref %s" % (datapath, B),
                    shell=True,
                    stderr=subprocess.DEVNULL,
                )
                .decode("ascii", "replace")
                .strip()
                .strip("* ")
            )
            return branch
        except:
            pass
    # If we couldn't find it locally, looking at all (local+remote)
    try:
        inp = (
            subprocess.check_output(
                "cd %s && git branch -a | awk -F ' +' '! /\(no branch\)/ {print $2}'"
                % datapath,
                shell=True,
                stderr=subprocess.DEVNULL,
            )
            .decode("ascii", "replace")
            .split()
        )
        if len(inp) > 0:
            for b in sorted(inp):
                if b.find("detached") == -1:
                    branch = str(b.replace("remotes/origin/", "", 1))
                    for B in wanted_branches:
                        if branch == B:
                            return branch
    except:
        pass

    # If still not found, resort to whatever branch comes first in the remote listing...
    inp = (
        subprocess.check_output(
            "cd %s && git ls-remote --heads %s" % (datapath, source["sourceURL"]),
            shell=True,
            stderr=subprocess.DEVNULL,
        )
        .decode("ascii", "replace")
        .split()
    )
    if len(inp) > 0:
        for remote in inp:
            m = re.match(r"[a-f0-9]+\s+refs/heads/(?:remotes/)?(.+)", remote)
            if m:
                branch = m.group(1)
                return branch
    # Give up
    return ""

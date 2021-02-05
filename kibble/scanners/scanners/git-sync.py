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

from kibble.configuration import conf
from kibble.scanners.utils import git

title = "Sync plugin for Git repositories"
version = "0.1.2"


def accepts(source):
    """ Do we accept this source? """
    if source["type"] == "git":
        return True
    # There are cases where we have a github repo, but don't wanna analyze the code, just issues
    if source["type"] == "github" and source.get("issuesonly", False) is False:
        return True
    return False


def scan(kibble_bit, source):

    # Get some vars, construct a data path for the repo
    path = source["sourceID"]
    url = source["sourceURL"]
    rootpath = "%s/%s/git" % (
        conf.get("scanner", "scratchdir"),
        source["organisation"],
    )

    # If the root path does not exist, try to make it recursively.
    if not os.path.exists(rootpath):
        try:
            os.makedirs(rootpath, exist_ok=True)
            print("Created root path %s" % rootpath)
        except:  # pylint: disable=bare-except
            source["steps"]["sync"] = {
                "time": time.time(),
                "status": "Could not create root scratch dir - permision denied?",
                "running": False,
                "good": False,
            }
            kibble_bit.update_source(source)
            return

    # This is were the repo should be cloned
    datapath = os.path.join(rootpath, path)

    kibble_bit.pprint("Checking out %s as %s" % (url, path))

    try:
        source["steps"]["sync"] = {
            "time": time.time(),
            "status": "Fetching code data from source location...",
            "running": True,
            "good": True,
        }
        kibble_bit.update_source(source)

        # If we already checked this out earlier, just sync it.
        if os.path.exists(datapath):
            kibble_bit.pprint("Repo %s exists, fetching changes..." % datapath)

            # Do we have a default branch here?
            branch = git.default_branch(source, datapath)
            if len(branch) == 0:
                source["default_branch"] = branch
                source["steps"]["sync"] = {
                    "time": time.time(),
                    "status": "Could not sync with source",
                    "exception": "No default branch was found in this repository",
                    "running": False,
                    "good": False,
                }
                kibble_bit.update_source(source)
                kibble_bit.pprint(
                    "No default branch found for %s (%s)"
                    % (source["sourceID"], source["sourceURL"])
                )
                return

            kibble_bit.pprint("Using branch %s" % branch)
            # Try twice checking out the main branch and fetching changes.
            # Sometimes we need to clean up after older scanners, which is
            # why we try twice. If first attempt fails, clean up and try again.
            for n in range(0, 2):
                try:
                    subprocess.check_output(
                        "GIT_TERMINAL_PROMPT=0 cd %s && git checkout %s && git fetch --all && git merge -X theirs --no-edit"
                        % (datapath, branch),
                        shell=True,
                        stderr=subprocess.STDOUT,
                    )
                    break
                except subprocess.CalledProcessError as err:
                    e = str(err.output).lower()
                    # We're interested in merge conflicts, which we can resolve through trickery.
                    if n > 0 or not (
                        "resolve" in e or "merge" in e or "overwritten" in e
                    ):
                        # This isn't a merge conflict, pass it to outer func
                        raise err
                    else:
                        # Switch to first commit
                        fcommit = subprocess.check_output(
                            "cd %s && git rev-list --max-parents=0 --abbrev-commit HEAD"
                            % datapath,
                            shell=True,
                            stderr=subprocess.STDOUT,
                        )
                        fcommit = fcommit.decode("ascii").strip()
                        subprocess.check_call(
                            "cd %s && git reset --hard %s" % (datapath, fcommit),
                            shell=True,
                            stderr=subprocess.STDOUT,
                        )
                        try:
                            subprocess.check_call(
                                "cd %s && git clean -xfd" % datpath,
                                shell=True,
                                stderr=subprocess.STDOUT,
                            )
                        except:  # pylint: disable=bare-except
                            pass
        # This is a new repo, clone it!
        else:
            kibble_bit.pprint("%s is new, cloning...!" % datapath)
            subprocess.check_output(
                "GIT_TERMINAL_PROMPT=0 cd %s && git clone %s %s"
                % (rootpath, url, path),
                shell=True,
                stderr=subprocess.STDOUT,
            )

    except subprocess.CalledProcessError as err:
        kibble_bit.pprint("Repository sync failed (no master?)")
        kibble_bit.pprint(str(err.output))
        source["steps"]["sync"] = {
            "time": time.time(),
            "status": "Sync failed at "
            + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()),
            "running": False,
            "good": False,
            "exception": str(err.output),
        }
        kibble_bit.update_source(source)
        return

    # All good, yay!
    source["steps"]["sync"] = {
        "time": time.time(),
        "status": "Source code fetched successfully at "
        + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()),
        "running": False,
        "good": True,
    }
    kibble_bit.update_source(source)

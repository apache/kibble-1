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
from kibble.scanners.scanners.base_scanner import BaseScanner
from kibble.scanners.utils import git, sloc


class GitSlocScanner(BaseScanner):
    """Source Lines of Code counter for Git"""

    title = "SloC Counter for Git"
    version = "0.1.0"

    @property
    def accepts(self):
        """ Do we accept this source? """
        if self.source["type"] == "git":
            return True
        # There are cases where we have a github repo, but don't wanna analyze the code, just issues
        if self.source["type"] == "github" and self.source.get("issuesonly"):
            return True
        return False

    def scan(self):
        source = self.source
        source_id = source["sourceID"]

        url = source["sourceURL"]
        root_path = (
            f'{conf.get("scanner", "scratchdir")}/{source["organisation"]}/{git}'
        )
        gpath = os.path.join(root_path, source_id)

        if not source["steps"]["sync"]["good"] or not os.path.exists(gpath):
            return

        source["steps"]["count"] = {
            "time": time.time(),
            "status": "SLoC count started at "
            + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()),
            "running": True,
            "good": True,
        }
        self.kibble_bit.update_source(source)

        try:
            branch = git.default_branch(source, gpath)
            subprocess.call("cd %s && git checkout %s" % (gpath, branch), shell=True)
        except:  # pylint: disable=bare-except
            self.log.error("SLoC counter failed to find main branch for %s", url)
            return False

        self.log.info("Running SLoC count for %s", url)
        languages, code_count, comment, blank, years, cost = sloc.count(gpath)

        source["sloc"] = {
            "sourceID": source_id,
            "loc": code_count,
            "comments": comment,
            "blanks": blank,
            "years": years,
            "cost": cost,
            "languages": languages,
        }
        source["steps"]["count"] = {
            "time": time.time(),
            "status": "SLoC count completed at "
            + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()),
            "running": False,
            "good": True,
        }
        self.kibble_bit.update_source(source)

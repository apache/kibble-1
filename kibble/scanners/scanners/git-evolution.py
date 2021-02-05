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

""" Git Evolution scanner """
import calendar
import datetime
import hashlib
import os
import subprocess
import time

from kibble.configuration import conf
from kibble.scanners.utils import sloc

title = "Git Evolution Scanner"
version = "0.1.0"


def accepts(source):
    """ Do we accept this source? """
    if source["type"] == "git":
        return True
    # There are cases where we have a github repo, but don't wanna analyze the code, just issues
    if source["type"] == "github" and source.get("issuesonly", False) == False:
        return True
    return False


def get_first_ref(gpath):
    try:
        return subprocess.check_output(
            "cd %s && git log `git rev-list --max-parents=0 HEAD` --pretty=format:%%ct"
            % gpath,
            shell=True,
        )
    except:  # pylint: disable=bare-except
        print("Could not get first ref, exiting!")
        return None


def acquire(kibble_bit, source):
    source["steps"]["evolution"] = {
        "time": time.time(),
        "status": "Evolution scan started at "
        + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()),
        "running": True,
        "good": True,
    }
    kibble_bit.update_source(source)


def release(kibble_bit, source, status, exception=None, good=False):
    source["steps"]["evolution"] = {
        "time": time.time(),
        "status": status,
        "running": False,
        "good": good,
    }

    if exception:
        source["steps"]["evolution"].update({"exception": exception})
    kibble_bit.update_source(source)


def check_branch(gpath, date, branch):
    try:
        subprocess.check_call(
            'cd %s && git rev-list -n 1 --before="%s" %s' % (gpath, date, branch),
            shell=True,
        )
        return True
    except:  # pylint: disable=bare-except
        return False


def checkout(gpath, date, branch):
    # print("Ready to cloc...checking out %s " % date)
    try:
        ref = (
            subprocess.check_output(
                'cd %s && git rev-list -n 1 --before="%s" "%s"' % (gpath, date, branch),
                shell=True,
                stderr=subprocess.STDOUT,
            )
            .decode("ascii", "replace")
            .strip()
        )
        subprocess.check_output(
            "cd %s && git checkout %s -- " % (gpath, ref),
            shell=True,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as err:
        print(err.output)


def find_branch(date, gpath):
    try:
        os.chdir(gpath)
        subprocess.check_call(
            'cd %s && git rev-list -n 1 --before="%s" master' % (gpath, date),
            shell=True,
            stderr=subprocess.DEVNULL,
        )
        return "master"
    except:  # pylint: disable=bare-except
        os.chdir(gpath)
        try:
            return (
                subprocess.check_output(
                    "cd %s && git rev-parse --abbrev-ref HEAD" % gpath,
                    shell=True,
                    stderr=subprocess.DEVNULL,
                )
                .decode("ascii", "replace")
                .strip()
                .strip("* ")
            )
        except:  # pylint: disable=bare-except
            # print("meh! no branch")
            return None


def scan(kibble_bit, source):

    rid = source["sourceID"]
    rootpath = "%s/%s/git" % (
        conf.get("scanner", "scratchdir"),
        source["organisation"],
    )
    gpath = os.path.join(rootpath, rid)

    gname = source["sourceID"]
    kibble_bit.pprint("Doing evolution scan of %s" % gname)

    inp = get_first_ref(gpath)
    if inp:
        ts = int(inp.split()[0])
        ts -= ts % 86400
        date = time.strftime("%Y-%b-%d 0:00", time.gmtime(ts))

        # print("Starting from %s" % date)
        now = time.time()

        rid = source["sourceID"]
        url = source["sourceURL"]
        rootpath = "%s/%s/git" % (
            conf.get("scanner", "scratchdir"),
            source["organisation"],
        )
        gpath = os.path.join(rootpath, rid)

        if source["steps"]["sync"]["good"] and os.path.exists(gpath):
            acquire(kibble_bit, source)
            branch = find_branch(date, gpath)

            if not branch:
                release(
                    source,
                    "Could not do evolutionary scan of code",
                    "No default branch was found in this repository",
                )
                return

            branch_exists = check_branch(gpath, date, branch)

            if not branch_exists:
                kibble_bit.pprint("Not trunk either (bad repo?), skipping")
                release(
                    source,
                    "Could not do evolutionary scan of code",
                    "No default branch was found in this repository",
                )
                return

            try:

                d = time.gmtime(now)
                year = d[0]
                quarter = d[1] - (d[1] % 3)
                if quarter <= 0:
                    quarter += 12
                    year -= 1
                while now > ts:
                    pd = (
                        datetime.datetime(year, quarter, 1)
                        .replace(tzinfo=datetime.timezone.utc)
                        .timetuple()
                    )
                    date = time.strftime("%Y-%b-%d 0:00", pd)
                    unix = calendar.timegm(pd)

                    # Skip the dates we've already processed
                    dhash = hashlib.sha224(
                        (source["sourceID"] + date).encode("ascii", "replace")
                    ).hexdigest()
                    found = kibble_bit.exists("evolution", dhash)
                    if not found:
                        checkout(gpath, date, branch)
                        kibble_bit.pprint(
                            "Running cloc on %s (%s) at %s"
                            % (gname, source["sourceURL"], date)
                        )
                        languages, codecount, comment, blank, years, cost = sloc.count(
                            gpath
                        )
                        js = {
                            "time": unix,
                            "sourceID": source["sourceID"],
                            "sourceURL": source["sourceURL"],
                            "organisation": source["organisation"],
                            "loc": codecount,
                            "comments": comment,
                            "blank": blank,
                            "years": years,
                            "cost": cost,
                            "languages": languages,
                        }
                        kibble_bit.index("evolution", dhash, js)
                    quarter -= 3
                    if quarter <= 0:
                        quarter += 12
                        year -= 1

                    # decrease month by 3
                    now = time.mktime(datetime.date(year, quarter, 1).timetuple())
            except Exception as e:
                kibble_bit.pprint(e)
                release(
                    kibble_bit,
                    source,
                    "Evolution scan failed at "
                    + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()),
                    str(e),
                )
                return

            release(
                kibble_bit,
                source,
                "Evolution scan completed at "
                + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()),
                good=True,
            )

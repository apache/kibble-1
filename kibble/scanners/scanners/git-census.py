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

import datetime
import email.utils
import hashlib
import os
import re
import subprocess
import tempfile
import time

title = "Census Scanner for Git"
version = "0.1.0"


def accepts(source):
    """ Do we accept this source?? """
    if source["type"] == "git":
        return True
    # There are cases where we have a github repo, but don't wanna analyze the code, just issues
    if source["type"] == "github" and source.get("issuesonly", False) == False:
        return True
    return False


def scan(KibbleBit, source):
    """ Conduct a census scan """
    people = {}
    idseries = {}
    lcseries = {}
    alcseries = {}
    ctseries = {}
    atseries = {}

    rid = source["sourceID"]
    url = source["sourceURL"]
    rootpath = "%s/%s/git" % (
        KibbleBit.config["scanner"]["scratchdir"],
        source["organisation"],
    )
    gpath = os.path.join(rootpath, rid)

    if "steps" in source and source["steps"]["sync"]["good"] and os.path.exists(gpath):
        source["steps"]["census"] = {
            "time": time.time(),
            "status": "Census count started at "
            + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()),
            "running": True,
            "good": True,
        }
        KibbleBit.updateSource(source)
        gname = rid
        inp = ""
        modificationDates = {}
        # Did we do a census before?
        if "census" in source and source["census"] > 0:
            # Go back 2 months, meh...
            ts = source["census"] - (62 * 86400)
            pd = time.gmtime(ts)
            date = time.strftime("%Y-%b-%d 0:00", pd)
            inp = subprocess.check_output(
                'git --git-dir %s/.git log --after="%s" --all "--pretty=format:::%%H|%%ce|%%cn|%%ae|%%an|%%ct" --numstat'
                % (gpath, date),
                shell=True,
            )
        else:
            inp = subprocess.check_output(
                'git --git-dir %s/.git log --all "--pretty=format:::%%H|%%ce|%%cn|%%ae|%%an|%%ct" --numstat'
                % gpath,
                shell=True,
            )
        tmp = tempfile.NamedTemporaryFile(mode="w+b", buffering=1, delete=False)
        tmp.write(inp)
        tmp.flush()
        tmp.close()
        with open(tmp.name, mode="r", encoding="utf-8", errors="replace") as f:
            inp = f.read()
            f.close()
        os.unlink(tmp.name)
        KibbleBit.pprint("Parsing log for %s (%s)..." % (rid, url))
        for m in re.finditer(
            u":([a-f0-9]+)\|([^\r\n|]+)\|([^\r\n|]+)\|([^\r\n|]+)\|([^\r\n|]+)\|([\d+]+)\r?\n([^:]+?):",
            inp,
            flags=re.MULTILINE,
        ):
            if m:
                ch = m.group(1)
                ce = m.group(2)
                cn = m.group(3)
                ae = m.group(4)
                an = m.group(5)
                ct = int(m.group(6))
                diff = m.group(7)
                insert = 0
                delete = 0
                files_touched = set()
                # Diffs
                for l in re.finditer(
                    u"(\d+)[ \t]+(\d+)[ \t]+([^\r\n]+)", diff, flags=re.MULTILINE
                ):
                    insert += int(l.group(1))
                    delete += int(l.group(2))
                    filename = l.group(3)
                    if filename:
                        files_touched.update([filename])
                    if (
                        filename
                        and len(filename) > 0
                        and (
                            not filename in modificationDates
                            or modificationDates[filename]["timestamp"] < ct
                        )
                    ):
                        modificationDates[filename] = {
                            "hash": ch,
                            "filename": filename,
                            "timestamp": ct,
                            "created": ct
                            if (
                                not filename in modificationDates
                                or not "created" in modificationDates[filename]
                                or modificationDates[filename]["created"] > ct
                            )
                            else modificationDates[filename]["created"],
                            "author_email": ae,
                            "committer_email": ce,
                        }
                    if insert > 100000000:
                        insert = 0
                    if delete > 100000000:
                        delete = 0
                    if delete > 1000000 or insert > 1000000:
                        KibbleBit.pprint(
                            "gigantic diff for %s (%s), ignoring"
                            % (gpath, source["sourceURL"])
                        )
                        pass
                if not gname in idseries:
                    idseries[gname] = {}
                if not gname in lcseries:
                    lcseries[gname] = {}
                if not gname in alcseries:
                    alcseries[gname] = {}
                if not gname in ctseries:
                    ctseries[gname] = {}
                if not gname in atseries:
                    atseries[gname] = {}
                ts = ct - (ct % 86400)
                if not ts in idseries[gname]:
                    idseries[gname][ts] = [0, 0]

                idseries[gname][ts][0] += insert
                idseries[gname][ts][1] += delete

                if not ts in lcseries[gname]:
                    lcseries[gname][ts] = {}
                if not ts in alcseries[gname]:
                    alcseries[gname][ts] = {}
                if not ce in lcseries[gname][ts]:
                    lcseries[gname][ts][ce] = [0, 0]
                lcseries[gname][ts][ce][0] += insert
                lcseries[gname][ts][ce][1] = lcseries[gname][ts][ce][0] + delete

                if not ae in alcseries[gname][ts]:
                    alcseries[gname][ts][ae] = [0, 0]
                alcseries[gname][ts][ae][0] += insert
                alcseries[gname][ts][ae][1] = alcseries[gname][ts][ae][0] + delete

                if not ts in ctseries[gname]:
                    ctseries[gname][ts] = {}
                if not ts in atseries[gname]:
                    atseries[gname][ts] = {}

                if not ce in ctseries[gname][ts]:
                    ctseries[gname][ts][ce] = 0
                ctseries[gname][ts][ce] += 1

                if not ae in atseries[gname][ts]:
                    atseries[gname][ts][ae] = 0
                atseries[gname][ts][ae] += 1

                # Committer
                if not ce in people or len(people[ce]["name"]) < len(cn):
                    people[ce] = people[ce] if ce in people else {"projects": [gname]}
                    people[ce]["name"] = cn
                    if not gname in people[ce]["projects"]:
                        people[ce]["projects"].append(gname)

                # Author
                if not ae in people or len(people[ae]["name"]) < len(an):
                    people[ae] = people[ae] if ae in people else {"projects": [gname]}
                    people[ae]["name"] = an
                    if not gname in people[ae]["projects"]:
                        people[ae]["projects"].append(gname)

                # Make a list of changed files, max 1024
                filelist = list(files_touched)
                filelist = filelist[:1023]

                # ES commit documents
                tsd = ts - (ts % 86400)
                js = {
                    "id": rid + "/" + ch,
                    "sourceID": rid,
                    "sourceURL": source["sourceURL"],
                    "organisation": source["organisation"],
                    "ts": ct,
                    "tsday": tsd,
                    "date": time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(ct)),
                    "committer_name": cn,
                    "committer_email": ce,
                    "author_name": an,
                    "author_email": ae,
                    "insertions": insert,
                    "deletions": delete,
                    "vcs": "git",
                    "files_changed": filelist,
                }
                jsx = {
                    "id": ch,
                    "organisation": source["organisation"],
                    "sourceID": source[
                        "sourceID"
                    ],  # Only ever the last source with this
                    "ts": ct,
                    "tsday": tsd,
                    "date": time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(ct)),
                    "committer_name": cn,
                    "committer_email": ce,
                    "author_name": an,
                    "author_email": ae,
                    "insertions": insert,
                    "deletions": delete,
                    "repository": rid,  # This will always ever only be the last repo that had it!
                    "vcs": "git",
                    "files_changed": filelist,
                }
                KibbleBit.append(
                    "person",
                    {
                        "upsert": True,
                        "name": cn,
                        "email": ce,
                        "address": ce,
                        "organisation": source["organisation"],
                        "id": hashlib.sha1(
                            ("%s%s" % (source["organisation"], ce)).encode(
                                "ascii", errors="replace"
                            )
                        ).hexdigest(),
                    },
                )
                KibbleBit.append(
                    "person",
                    {
                        "upsert": True,
                        "name": an,
                        "email": ae,
                        "address": ae,
                        "organisation": source["organisation"],
                        "id": hashlib.sha1(
                            ("%s%s" % (source["organisation"], ae)).encode(
                                "ascii", errors="replace"
                            )
                        ).hexdigest(),
                    },
                )
                KibbleBit.append("code_commit", js)
                KibbleBit.append("code_commit_unique", jsx)

        if True:  # Do file changes?? Might wanna make this optional
            KibbleBit.pprint("Scanning file changes for %s" % source["sourceURL"])
            for filename in modificationDates:
                fid = hashlib.sha1(
                    ("%s/%s" % (source["sourceID"], filename)).encode(
                        "ascii", errors="replace"
                    )
                ).hexdigest()
                jsfe = {
                    "upsert": True,
                    "id": fid,
                    "organisation": source["organisation"],
                    "sourceID": source["sourceID"],
                    "ts": modificationDates[filename]["timestamp"],
                    "date": time.strftime(
                        "%Y/%m/%d %H:%M:%S",
                        time.gmtime(modificationDates[filename]["timestamp"]),
                    ),
                    "committer_email": modificationDates[filename]["committer_email"],
                    "author_email": modificationDates[filename]["author_email"],
                    "hash": modificationDates[filename]["hash"],
                    "created": modificationDates[filename]["created"],
                    "createdDate": time.strftime(
                        "%Y/%m/%d %H:%M:%S",
                        time.gmtime(modificationDates[filename]["created"]),
                    ),
                }
                found = KibbleBit.exists("file_history", fid)
                if found:
                    del jsfe["created"]
                    del jsfe["createdDate"]
                KibbleBit.append("file_history", jsfe)

        source["steps"]["census"] = {
            "time": time.time(),
            "status": "Census count completed at "
            + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()),
            "running": False,
            "good": True,
        }
        source["census"] = time.time()
        KibbleBit.updateSource(source)

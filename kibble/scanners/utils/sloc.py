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

""" This is the SLoC counter utility for Kibble """

import multiprocessing
import re
import subprocess


def count(path):
    """ Count lines of Code """
    # We determine how many cores there are, and adjust the
    # process count based on that. Max 4 procs.
    my_core_count = min((4, int(multiprocessing.cpu_count())))
    inp = subprocess.check_output(
        "cloc --quiet --progress-rate=0 --processes=%u %s" % (my_core_count, path),
        shell=True,
    ).decode("ascii", "replace")
    m = re.search(
        r".*Language\s+files\s+blank\s+comment\s+code[\s\S]+?-+([\s\S]+?)-+[\s\S]+?SUM:\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)",
        inp,
        flags=re.MULTILINE | re.UNICODE,
    )
    languages = {}
    ccount = 0
    years = 0
    cost = 0
    codecount = ""
    comment = ""
    blank = ""
    if m:
        lingos = m.group(1)
        fcount = m.group(2)
        blank = m.group(3)
        comment = m.group(4)
        codecount = m.group(5)
        for lm in re.finditer(
            r"([A-Za-z +-/0-9]+)\s+\d+\s+(\d+)\s+(\d+)\s+(\d+)", lingos
        ):
            lang = lm.group(1).replace(" Header", "").lower()
            lang = re.sub(r"\s\s+", "", lang)
            lang = re.sub(r"^[Cc]\\?/", "", lang)
            lang = lang.replace(".", "_")
            if len(lang) > 0:
                C = 0
                D = 0
                E = 0
                if lang in languages:
                    C = languages[lang]["code"]
                    D = languages[lang]["comment"]
                    E = languages[lang]["blank"]
                languages[lang] = {
                    "code": int(lm.group(4)) + C,
                    "comment": int(lm.group(3)) + D,
                    "blank": int(lm.group(2)) + E,
                }
        ccount = int(codecount.replace(",", "")) + int(comment.replace(",", ""))
        codecount = int(codecount.replace(",,", ""))
        blank = int(blank.replace(",,", ""))
        comment = int(comment.replace(",,", ""))
        years = ccount / 3300.0
        cost = years * 72000
    return [languages, codecount, comment, blank, years, cost]

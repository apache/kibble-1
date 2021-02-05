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
import email.errors
import email.header
import email.utils
import hashlib
import mailbox
import os
import re
import time

from kibble.scanners.utils import urlmisc

title = "Scanner for GNU Mailman Pipermail"
version = "0.1.0"


def accepts(source):
    """ Whether or not we think this is pipermail """
    if source["type"] == "pipermail":
        return True
    if source["type"] == "mail":
        url = source["sourceURL"]
        pipermail = re.match(r"(https?://.+/(archives|pipermail)/.+?)/?$", url)
        if pipermail:
            return True
    return False


def scan(kibble_bit, source):
    url = source["sourceURL"]
    pipermail = re.match(r"(https?://.+/(archives|pipermail)/.+?)/?$", url)
    if pipermail:
        kibble_bit.pprint("Scanning Pipermail source %s" % url)
        skipped = 0

        source["steps"]["mail"] = {
            "time": time.time(),
            "status": "Downloading Pipermail statistics",
            "running": True,
            "good": True,
        }
        kibble_bit.update_source(source)

        dt = time.gmtime(time.time())
        first_year = 1970
        year = dt[0]
        month = dt[1]
        if month <= 0:
            month += 12
            year -= 1
        months = 0

        knowns = {}

        # While we have older archives, continue to parse
        month_names = [
            "December",
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        while first_year <= year:
            gzurl = "%s/%04u-%s.txt.gz" % (url, year, month_names[month])
            pd = datetime.date(year, month, 1).timetuple()
            dhash = hashlib.sha224(
                ("%s %s" % (source["organisation"], gzurl)).encode(
                    "ascii", errors="replace"
                )
            ).hexdigest()
            found = kibble_bit.exists("mailstats", dhash)
            if (
                months <= 1 or not found
            ):  # Always parse this month's stats and the previous month :)
                months += 1
                mailFile = urlmisc.unzip(gzurl)
                if mailFile:
                    try:
                        skipped = 0
                        messages = mailbox.mbox(mailFile)

                        rawtopics = {}
                        posters = {}
                        no_posters = 0
                        emails = 0
                        senders = {}
                        for message in messages:
                            emails += 1
                            sender = message["from"]
                            name = sender
                            if (
                                not "subject" in message
                                or not message["subject"]
                                or not "from" in message
                                or not message["from"]
                            ):
                                continue

                            irt = message.get("in-reply-to", None)
                            if not irt and message.get("references"):
                                irt = message.get("references").split("\n")[0].strip()
                            replyto = None
                            if irt and irt in senders:
                                replyto = senders[irt]
                                print("This is a reply to %s" % replyto)
                            raw_subject = re.sub(
                                r"^[a-zA-Z]+\s*:\s*", "", message["subject"], count=10
                            )
                            raw_subject = re.sub(
                                r"[\r\n\t]+", "", raw_subject, count=10
                            )
                            if raw_subject not in rawtopics:
                                rawtopics[raw_subject] = 0
                            rawtopics[raw_subject] += 1
                            m = re.match(
                                r"(.+?) at (.+?) \((.*)\)$",
                                message["from"],
                                flags=re.UNICODE,
                            )
                            if m:
                                name = m.group(3).strip()
                                sender = m.group(1) + "@" + m.group(2)
                            else:
                                m = re.match(
                                    r"(.+)\s*<(.+)>", message["from"], flags=re.UNICODE
                                )
                                if m:
                                    name = m.group(1).replace('"', "").strip()
                                    sender = m.group(2)
                            if sender not in posters:
                                posters[sender] = {"name": name, "email": sender}
                            senders[message.get("message-id", "??")] = sender
                            mdate = email.utils.parsedate_tz(message["date"])
                            mdatestring = time.strftime(
                                "%Y/%m/%d %H:%M:%S",
                                time.gmtime(email.utils.mktime_tz(mdate)),
                            )
                            if sender not in knowns:
                                sid = hashlib.sha1(
                                    ("%s%s" % (source["organisation"], sender)).encode(
                                        "ascii", errors="replace"
                                    )
                                ).hexdigest()
                                knowns[sender] = kibble_bit.exists("person", sid)
                            if sender not in knowns:
                                kibble_bit.append(
                                    "person",
                                    {
                                        "name": name,
                                        "email": sender,
                                        "organisation": source["organisation"],
                                        "id": hashlib.sha1(
                                            (
                                                "%s%s"
                                                % (source["organisation"], sender)
                                            ).encode("ascii", errors="replace")
                                        ).hexdigest(),
                                    },
                                )
                                knowns[sender] = True
                            jse = {
                                "organisation": source["organisation"],
                                "sourceURL": source["sourceURL"],
                                "sourceID": source["sourceID"],
                                "date": mdatestring,
                                "sender": sender,
                                "replyto": replyto,
                                "subject": message["subject"],
                                "address": sender,
                                "ts": email.utils.mktime_tz(mdate),
                                "id": message["message-id"],
                            }
                            kibble_bit.append("email", jse)

                        no_posters = len(posters)
                        topics = len(rawtopics)
                        i = 0
                        for key in reversed(sorted(rawtopics, key=lambda x: x)):
                            val = rawtopics[key]
                            i += 1
                            if i > 10:
                                break
                            kibble_bit.pprint(
                                "Found top 10: %s (%s emails)" % (key, val)
                            )
                            shash = hashlib.sha224(
                                key.encode("ascii", errors="replace")
                            ).hexdigest()
                            md = time.strftime("%Y/%m/%d %H:%M:%S", pd)
                            mlhash = hashlib.sha224(
                                (
                                    "%s%s%s%s"
                                    % (
                                        key,
                                        source["sourceURL"],
                                        source["organisation"],
                                        md,
                                    )
                                ).encode("ascii", errors="replace")
                            ).hexdigest()  # one unique id per month per mail thread
                            jst = {
                                "organisation": source["organisation"],
                                "sourceURL": source["sourceURL"],
                                "sourceID": source["sourceID"],
                                "date": md,
                                "emails": val,
                                "shash": shash,
                                "subject": key,
                                "ts": time.mktime(pd),
                                "id": mlhash,
                            }
                            kibble_bit.index("mailtop", mlhash, jst)

                        jso = {
                            "organisation": source["organisation"],
                            "sourceURL": source["sourceURL"],
                            "sourceID": source["sourceID"],
                            "date": time.strftime("%Y/%m/%d %H:%M:%S", pd),
                            "authors": no_posters,
                            "emails": emails,
                            "topics": topics,
                        }
                        kibble_bit.index("mailstats", dhash, jso)

                        os.unlink(mailFile)
                    except Exception as err:
                        kibble_bit.pprint(
                            "Couldn't parse %s, skipping: %s" % (gzurl, err)
                        )
                        skipped += 1
                        if skipped > 12:
                            kibble_bit.pprint(
                                "12 skips in a row, breaking off (no more data?)"
                            )
                            break
                else:
                    kibble_bit.pprint("Couldn't find %s, skipping." % gzurl)
                    skipped += 1
                    if skipped > 12:
                        kibble_bit.pprint(
                            "12 skips in a row, breaking off (no more data?)"
                        )
                        break
            month -= 1
            if month <= 0:
                month += 12
                year -= 1

        source["steps"]["mail"] = {
            "time": time.time(),
            "status": "Mail archives successfully scanned at "
            + time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(time.time())),
            "running": False,
            "good": True,
        }
        kibble_bit.update_source(source)
    else:
        kibble_bit.pprint("Invalid Pipermail URL detected: %s" % url, True)
        source["steps"]["mail"] = {
            "time": time.time(),
            "status": "Invalid or malformed URL detected!",
            "running": False,
            "good": False,
        }
        kibble_bit.update_source(source)

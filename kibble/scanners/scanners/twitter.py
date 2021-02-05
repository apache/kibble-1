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

"""
This is a Kibble scanner plugin for Twitter sources.
"""
import hashlib
import time

import twitter

title = "Scanner plugin for Twitter"
version = "0.1.0"


def accepts(source):
    """ Test if source matches a Twitter handle """
    # If the source equals the plugin name, assume a yes
    if source["type"] == "twitter":
        return True

    # Default to not recognizing the source
    return False


def get_followers(kibble_bit, source, t):
    """ Get followers of a handle, store them for mapping and trend purposes"""
    # Get our twitter handle
    handle = source["sourceURL"]

    # Get number of followers
    tuser = t.GetUser(screen_name=handle)
    no_followers = tuser.followers_count
    d = time.strftime("%Y/%m/%d 0:00:00", time.gmtime())  # Today at midnight
    dhash = hashlib.sha224(
        ("twitter:%s:%s:%s" % (source["organisation"], source["sourceURL"], d)).encode(
            "ascii", errors="replace"
        )
    ).hexdigest()
    jst = {
        "organisation": source["organisation"],
        "sourceURL": source["sourceURL"],
        "sourceID": source["sourceID"],
        "id": dhash,
        "followers": no_followers,
        "date": d,
    }
    kibble_bit.pprint("%s has %u followers currently." % (handle, no_followers))
    kibble_bit.index("twitter_followers", dhash, jst)

    # Collect list of current followers
    followers = t.GetFollowers(screen_name=handle)

    # For each follower, if they're not mapped yet, add them
    # This has a limitation of 100 new added per run, but meh...
    kibble_bit.pprint("Looking up followers of %s" % handle)
    for follower in followers:
        # id, name, screen_name are useful here
        kibble_bit.pprint("Found %s as follower" % follower.screen_name)

        # Store twitter follower profile if not already logged
        dhash = hashlib.sha224(
            ("twitter:%s:%s:%s" % (source["organisation"], handle, follower.id)).encode(
                "ascii", errors="replace"
            )
        ).hexdigest()
        if not kibble_bit.exists("twitter_follow", dhash):
            jst = {
                "organisation": source["organisation"],
                "sourceURL": source["sourceURL"],
                "sourceID": source["sourceID"],
                "twitterid": follower.id,
                "name": follower.name,
                "screenname": follower.screen_name,
                "id": dhash,
                "date": time.strftime(
                    "%Y/%m/%d %H:%M:%S", time.gmtime()
                ),  # First time we spotted them following.
            }
            kibble_bit.pprint(
                "%s is new, recording date and details." % follower.screen_name
            )
            kibble_bit.index("twitter_follow", dhash, jst)


def scan(kibble_bit, source):
    source["steps"]["twitter"] = {
        "time": time.time(),
        "status": "Scanning Twitter activity and status",
        "running": True,
        "good": True,
    }
    kibble_bit.update_source(source)
    t = None
    if "creds" in source and source["creds"]:
        t = twitter.Api(
            access_token_key=source["creds"].get("token", None),
            access_token_secret=source["creds"].get("token_secret", None),
            consumer_key=source["creds"].get("consumer_key", None),
            consumer_secret=source["creds"].get("consumer_secret", None),
        )
        kibble_bit.pprint("Verifying twitter credentials...")
        try:
            t.VerifyCredentials()
        except:  # pylint: disable=bare-except
            source["steps"]["twitter"] = {
                "time": time.time(),
                "status": "Could not verify twitter credentials",
                "running": False,
                "good": False,
            }
            kibble_bit.update_source(source)
            kibble_bit.pprint("Could not verify twitter creds, aborting!")
            return
    # Start by getting and saving followers
    try:
        get_followers(kibble_bit, source, t)
    except Exception as err:
        source["steps"]["twitter"] = {
            "time": time.time(),
            "status": "Could not scan Twitter: %s" % err,
            "running": False,
            "good": False,
        }
        kibble_bit.update_source(source)
        kibble_bit.pprint("Twitter scan failed: %s" % err)

    # All done, report that!
    source["steps"]["twitter"] = {
        "time": time.time(),
        "status": "Twitter successfully scanned at "
        + time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(time.time())),
        "running": False,
        "good": True,
    }
    kibble_bit.update_source(source)

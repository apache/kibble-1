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
This is a Kibble JSON API plugin.
"""
import requests
import time
import base64

CONNECT_TIMEOUT = 2  # Max timeout for the connect part of a request.


# Should be set low as it may otherwise freeze the scanner.
def get(url, cookie=None, auth=None, token=None, retries=5, timeout=30):
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Apache Kibble",
    }
    if auth:
        xcreds = auth.encode(encoding="ascii", errors="replace")
        bauth = (
            base64.encodebytes(xcreds)
            .decode("ascii", errors="replace")
            .replace("\n", "")
        )
        headers["Authorization"] = "Basic %s" % bauth
    if token:
        headers["Authorization"] = "token %s" % token
    if cookie:
        headers["Cookie"] = cookie
    rv = requests.get(url, headers=headers, timeout=(CONNECT_TIMEOUT, timeout))
    # Some services may be rate limited. We'll try sleeping it off in 60 second
    # intervals for a max of five minutes, then give up.
    if rv.status_code == 429:
        if retries > 0:
            time.sleep(60)
            retries -= 1
            return get(
                url,
                cookie=cookie,
                auth=auth,
                token=token,
                retries=retries,
                timeout=timeout,
            )
    if rv.status_code < 400:
        return rv.json()
    raise requests.exceptions.ConnectionError(
        "Could not fetch JSON, server responded with status code %u" % rv.status_code,
        response=rv,
    )


def gettxt(url, cookie=None, auth=None):
    """ Same as above, but returns as text blob """
    headers = {"Content-type": "application/json", "Accept": "*/*"}
    if auth:
        xcreds = auth.encode(encoding="ascii", errors="replace")
        bauth = (
            base64.encodebytes(xcreds)
            .decode("ascii", errors="replace")
            .replace("\n", "")
        )
        headers["Authorization"] = "Basic %s" % bauth
    if cookie:
        headers["Cookie"] = cookie
    rv = requests.get(url, headers=headers)
    js = rv.text
    if rv.status_code != 404:
        return js
    return None


def post(url, data, cookie=None, auth=None):
    headers = {
        "Content-type": "application/json",
        "Accept": "*/*",
        "User-Agent": "Apache Kibble",
    }
    if auth:
        xcreds = auth.encode(encoding="ascii", errors="replace")
        bauth = (
            base64.encodebytes(xcreds)
            .decode("ascii", errors="replace")
            .replace("\n", "")
        )
        headers["Authorization"] = "Basic %s" % bauth
    if cookie:
        headers["Cookie"] = cookie
    rv = requests.post(url, headers=headers, json=data)
    js = rv.json()
    return js

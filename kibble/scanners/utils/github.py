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

""" GitHub utility library """
import re
import requests
import time

repo_pattern = re.compile(".*[:/]([^/]+)/([^/]+).git")
issues_api = "https://api.github.com/repos/%s/%s/issues"
traffic_api = "https://api.github.com/repos/%s/%s/traffic"
popular_api = "https://api.github.com/repos/%s/%s/popular"
rate_limit_api = "https://api.github.com/rate_limit"


def get_limited(url, params=None, auth=None):
    """ Get a GitHub API response, keeping in mind that we may
        be rate-limited by the abuse system """
    number_of_retries = 0
    resp = requests.get(url, params=params, auth=auth)
    while resp.status_code == 403 and number_of_retries < 20:
        js = resp.json()
        # If abuse-detection kicks in, sleep it off
        if "You have triggered an abuse" in js["message"]:
            time.sleep(5)
            number_of_retries += 1
            resp = requests.get(url, params=params, auth=auth)
        else:
            break
    resp.raise_for_status()
    return resp.json()


def get_tokens_left(auth=None):
    """ Gets number of GitHub tokens left this hour... """
    js = get_limited(rate_limit_api, auth=auth)
    tokens_left = js["rate"]["remaining"]
    return tokens_left


def issues(source, params={}, auth=None):
    local_params = {"per_page": 100, "page": 1}
    local_params.update(params)

    repo_user = repo_pattern.findall(source["sourceURL"])[0]
    return get_limited(issues_api % repo_user, params=local_params, auth=auth)


def views(source, auth=None):
    repo_user = repo_pattern.findall(source["sourceURL"])[0]
    return get_limited("%s/views" % (traffic_api % repo_user), auth=auth)


def clones(source, auth=None):
    repo_user = repo_pattern.findall(source["sourceURL"])[0]
    return get_limited("%s/clones" % (traffic_api % repo_user), auth=auth)


def referrers(source, auth=None):
    repo_user = repo_pattern.findall(source["sourceURL"])[0]
    return get_limited("%s/referrers" % (popular_api % repo_user), auth=auth)


def user(user_url, auth=None):
    return get_limited(user_url, auth=auth)


def get_all(source, f, params={}, auth=None):
    acc = []
    page = params.get("page", 1)

    while True:
        time.sleep(1.5)
        items = f(source, params=params, auth=auth)
        if not items:
            break

        acc.extend(items)

        page = page + 1
        params.update({"page": page})

    return acc

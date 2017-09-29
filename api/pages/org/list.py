#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This is the Org list renderer for Kibble
"""

import json
import time

def run(API, environ, indata, session):
    now = time.time()
    # We need to be logged in for this!
    if not session.user:
        raise API.exception(403, "You must be logged in to use this API endpoint! %s")
    
    ####################################################################
    orgs = []
    if session.user['userlevel'] == "admin":
        res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="organisation",
            body = {'query': { 'match_all': {}}}
        )
        for doc in res['hits']['hits']:
            orgs.append(doc['_source'])
    else:
        res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="organisation",
            body = {'query': { 'terms': {'id': session.user['organisations']}}}
        )
        for doc in res['hits']['hits']:
            orgs.append(doc['_source'])
    
    
    JSON_OUT = {
        'organisations': orgs,
        'okay': True,
        'responseTime': time.time() - now
    }
    yield json.dumps(JSON_OUT)

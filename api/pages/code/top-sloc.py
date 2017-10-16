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
########################################################################
# OPENAPI-URI: /api/code/top-sloc
########################################################################
# get:
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Timeseries'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Shows top 25 repos by lines of code
# post:
#   requestBody:
#     content:
#       application/json:
#         schema:
#           $ref: '#/components/schemas/defaultWidgetArgs'
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Timeseries'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Shows top 25 repos by lines of code
# 
########################################################################





"""
This is the TopN repos by SLoC list renderer for Kibble
"""

import json
import time
import re

def run(API, environ, indata, session):
    
    # We need to be logged in for this!
    if not session.user:
        raise API.exception(403, "You must be logged in to use this API endpoint! %s")
    
    now = time.time()
    
    # First, fetch the view if we have such a thing enabled
    viewList = []
    if indata.get('view'):
        viewList = session.getView(indata.get('view'))
    if indata.get('subfilter'):
        viewList = session.subFilter(indata.get('subfilter'), view = viewList) 
    
    
    ####################################################################
    ####################################################################
    dOrg = session.user['defaultOrganisation'] or "apache"
    query = {
                'query': {
                    'bool': {
                        'must': [
                            {'terms':
                                {
                                    'type': ['git', 'svn', 'github']
                                }
                            },
                            {
                                'term': {
                                    'organisation': dOrg
                                }
                            }
                        ]
                    }
                }
            }
    # Source-specific or view-specific??
    if indata.get('source'):
        query['query']['bool']['must'].append({'term': {'sourceID': indata.get('source')}})
    elif viewList:
        query['query']['bool']['must'].append({'terms': {'sourceID': viewList}})
    
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="source",
            size = 5000,
            body = query
        )
    
    toprepos = []
    for doc in res['hits']['hits']:
        repo = doc['_source']
        url = re.sub(r".+/([^/]+?)(?:\.git)?$", r"\1", repo['sourceURL'])
        if 'sloc' in repo:
            count = repo['sloc'].get('loc', 0)
            if not count:
                count = 0
            toprepos.append([url, count])
        
    toprepos = sorted(toprepos, key = lambda x: int(x[1]), reverse = True)
    top = toprepos[0:24]
    if len(toprepos) > 25:
        count = 0
        for repo in toprepos[25:]:
            count += repo[1]
        top.append(["Other repos", count])
    
    tophash = {}
    for v in top:
        tophash[v[0]] = v[1]
        
    JSON_OUT = {
        'counts': tophash,
        'okay': True,
        'responseTime': time.time() - now,
    }
    yield json.dumps(JSON_OUT)

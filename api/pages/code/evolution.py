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
# OPENAPI-URI: /api/code/evolution
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
#   summary: Show code evolution as a timeseries
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
#   summary: Show code evolution as a timeseries
# 
########################################################################





"""
This is the TopN committers list renderer for Kibble
"""

import json
import time
import hashlib

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
    
    
    breakdown = False
    onlycode = False
    
    
    ####################################################################
    ####################################################################
    dOrg = session.user['defaultOrganisation'] or "apache"
    query = {
                'query': {
                    'bool': {
                        'must': [
                            {'range':
                                {
                                    'time': {
                                        'from': 0,
                                        'to': int(time.time())
                                    }
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
    
    # We need scrolling here!
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="evolution",
            scroll = '2m',
            size = 5000,
            body = query
        )
    sid = res['_scroll_id']
    scroll_size = res['hits']['total']
    if type(scroll_size) is dict:
        scroll_size = scroll_size['value'] # ES >= 7.x
    
    timeseries = []
    tstmp = {}
    
    while (scroll_size > 0):
        for doc in res['hits']['hits']:
            updates = doc['_source']
            ts = updates['time'] #round(updates['time']/86400) * 86400
            if updates['time'] % 86400 != 0:
                continue
            tstmp[ts] = tstmp.get(ts, {})
            item = tstmp[ts]
            if breakdown:
                pass
            else:
                item['code'] = item.get('code', 0) + (updates['loc'] or 0)
                item['comments'] = item.get('comments', 0) + (updates['comments'] or 0)
                item['blanks'] = item.get('blanks', 0) + (updates['blank'] or 0)
                
        res = session.DB.ES.scroll(scroll_id = sid, scroll = '1m')
        sid = res['_scroll_id']
        scroll_size = len(res['hits']['hits'])
    
    for k, v in tstmp.items():
        v['date'] = k
        timeseries.append(v)
        
    timeseries = sorted(timeseries, key = lambda x: x['date'])
    JSON_OUT = {
        'widgetType': {
            'chartType': 'line',  # Recommendation for the UI
            'stack': True
        },
        'timeseries': timeseries,
        'sortOrder': ['code', 'comments', 'blanks'],
        'okay': True,
        'responseTime': time.time() - now
    }
    yield json.dumps(JSON_OUT)

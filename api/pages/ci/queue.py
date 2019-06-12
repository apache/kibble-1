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
# OPENAPI-URI: /api/ci/queue
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
#   summary: Shows email sent over time
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
#   summary: Shows CI queue over time
# 
########################################################################



"""
This is the CI queue timeseries renderer for Kibble
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
    
    # We only want build sources, so we can sum up later.
    viewList = session.subType(['jenkins', 'travis', 'buildbot'], viewList)
    
    dateTo = indata.get('to', int(time.time()))
    dateFrom = indata.get('from', dateTo - (86400*30*6)) # Default to a 6 month span
    
    interval = indata.get('interval', 'month')
    
    
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
                                        'from': dateFrom,
                                        'to': dateTo
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
        viewList = [indata.get('source')]
    
    query['query']['bool']['must'].append({'term': {'sourceID': 'x'}})
    
    timeseries = []
    for source in viewList:
        query['query']['bool']['must'][2] = {'term': {'sourceID': source}}
        
        # Get queue stats
        query['aggs'] = {
                'timeseries': {
                    'date_histogram': {
                        'field': 'date',
                        'interval': interval
                    },
                    'aggs': {
                        'size': {
                            'avg': {
                                'field': 'size'
                            }
                        },
                        'blocked': {
                            'avg': {
                                'field': 'blocked'
                            }
                        },
                        'building': {
                            'avg': {
                                'field': 'building'
                            }
                        },
                        'stuck': {
                            'avg': {
                                'field': 'stuck'
                            }
                        },
                        'wait': {
                            'avg': {
                                'field': 'avgwait'
                            }
                        }
                    }
                }
            }
        res = session.DB.ES.search(
                index=session.DB.dbname,
                doc_type="ci_queue",
                size = 0,
                body = query
            )

        for bucket in res['aggregations']['timeseries']['buckets']:
            ts = int(bucket['key'] / 1000)
            bucket['wait']['value'] = bucket['wait'].get('value', 0) or 0
            if bucket['doc_count'] == 0:
                continue
            
            found = False
            for t in timeseries:
                if t['date'] == ts:
                    found = True
                    t['queue size'] += bucket['size']['value']
                    t['builds running'] += bucket['building']['value']
                    t['average wait (hours)'] += bucket['wait']['value']
                    t['builders'] += 1
            if not found:
                timeseries.append({
                    'date': ts,
                    'queue size': bucket['size']['value'],
                    'builds running': bucket['building']['value'],
                    'average wait (hours)': bucket['wait']['value'],
                    'builders': 1,
                })
    
    for t in timeseries:
        t['average wait (hours)'] = int(t['average wait (hours)']/360)/10.0
        del t['builders']
        
    JSON_OUT = {
        'widgetType': {
            'chartType': 'line',  # Recommendation for the UI
            'nofill': True
        },
        'timeseries': timeseries,
        'interval': interval,
        'okay': True,
        'responseTime': time.time() - now
    }
    yield json.dumps(JSON_OUT)

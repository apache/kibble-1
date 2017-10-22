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
# OPENAPI-URI: /api/issue/issues
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
#   summary: Shows timeseries of issues opened/closed over time
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
#   summary: Shows timeseries of issues opened/closed over time
# 
########################################################################





"""
This is the issue timeseries renderer for Kibble
"""

import json
import time
import hashlib

# This creates an empty timeseries object with
# all categories initialized as 0 opened, 0 closed.
def makeTS(dist):
    ts = {}
    for k in dist:
        ts[k + ' opened'] = 0
        ts[k + ' closed'] = 0
    return ts

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
    
    
    dateTo = indata.get('to', int(time.time()))
    dateFrom = indata.get('from', dateTo - (86400*30*6)) # Default to a 6 month span
    
    interval = indata.get('interval', 'month')
    
    # By default, we lump PRs and issues into the same category
    distinct = {
        'issues': ['issue', 'pullrequest']
    }
    
    # If requested, we split them into two
    if indata.get('distinguish', False):
        distinct = {
            'issues':        ['issue'],
            'pull requests': ['pullrequest']
        }
    
    timeseries = {}
    
    # For each category and the issue types that go along with that,
    # grab opened and closed over time.
    for iType, iValues in distinct.items():
        ####################################################################
        # ISSUES OPENED                                                    #
        ####################################################################
        dOrg = session.user['defaultOrganisation'] or "apache"
        query = {
                    'query': {
                        'bool': {
                            'must': [
                                {'range':
                                    {
                                        'created': {
                                            'from': dateFrom,
                                            'to': dateTo
                                        }
                                    }
                                },
                                {
                                    'term': {
                                        'organisation': dOrg
                                    }
                                },
                                {
                                    'terms': {
                                        'issuetype': iValues
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
        if indata.get('email'):
            query['query']['bool']['must'].append({'term': {'issueCreator': indata.get('email')}})
        
        # Get number of opened ones, this period
        query['aggs'] = {
                'commits': {
                    'date_histogram': {
                        'field': 'createdDate',
                        'interval': interval
                    }                
                }
            }
        res = session.DB.ES.search(
                index=session.DB.dbname,
                doc_type="issue",
                size = 0,
                body = query
            )
        
        for bucket in res['aggregations']['commits']['buckets']:
            ts = int(bucket['key'] / 1000)
            count = bucket['doc_count']
            timeseries[ts] = timeseries.get(ts, makeTS(distinct))
            timeseries[ts][iType + ' opened'] = timeseries[ts].get(iType + ' opened', 0) + count
            
        
        ####################################################################
        # ISSUES CLOSED                                                    #
        ####################################################################
        dOrg = session.user['defaultOrganisation'] or "apache"
        query = {
                    'query': {
                        'bool': {
                            'must': [
                                {'range':
                                    {
                                        'closed': {
                                            'from': dateFrom,
                                            'to': dateTo
                                        }
                                    }
                                },
                                {
                                    'term': {
                                        'organisation': dOrg
                                    }
                                },
                                {
                                    'terms': {
                                        'issuetype': iValues
                                    }
                                }
                            ]
                        }
                    }
                }
        if viewList:
            query['query']['bool']['must'].append({'terms': {'sourceID': viewList}})
        if indata.get('source'):
            query['query']['bool']['must'].append({'term': {'sourceID': indata.get('source')}})
        if indata.get('email'):
            query['query']['bool']['must'].append({'term': {'issueCloser': indata.get('email')}})
        
        # Get number of closed ones, this period
        query['aggs'] = {
                'commits': {
                    'date_histogram': {
                        'field': 'closedDate',
                        'interval': interval
                    }                
                }
            }
        res = session.DB.ES.search(
                index=session.DB.dbname,
                doc_type="issue",
                size = 0,
                body = query
            )
        
        for bucket in res['aggregations']['commits']['buckets']:
            ts = int(bucket['key'] / 1000)
            count = bucket['doc_count']
            timeseries[ts] = timeseries.get(ts, makeTS(distinct))
            timeseries[ts][iType + ' closed'] = timeseries[ts].get(iType + ' closed', 0) + count
        
    ts = []
    for k, v in timeseries.items():
        v['date'] = k
        ts.append(v)
        
    
    JSON_OUT = {
        'widgetType': {
            'chartType': 'line',  # Recommendation for the UI
            'nofill': True
        },
        'timeseries': ts,
        'interval': interval,
        'okay': True,
        'distinguishable': True,
        'responseTime': time.time() - now
    }
    yield json.dumps(JSON_OUT)

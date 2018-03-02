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
# OPENAPI-URI: /api/forum/issues
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
#   summary: Shows timeseries of forum topics opened/responded-to over time
# 
########################################################################





"""
This is the forum timeseries renderer for Kibble
"""

import json
import time
import hashlib

# This creates an empty timeseries object with
# all categories initialized as 0 opened, 0 closed.
def makeTS(dist):
    ts = {}
    for k in dist:
        ts[k + ' topics'] = 0
        ts[k + ' replies'] = 0
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
    
    # By default, we lump generic forums and question/answer (like SO, askbot) together as one
    distinct = {
        'forum': ['discourse', 'stackoverflow', 'askbot']
    }
    
    # If requested, we split them into two
    if indata.get('distinguish', False):
        distinct = {
            'forum':        ['discourse'],
            'question bank': ['stackoverflow', 'askbot']
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
                                        'type': iValues
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
            query['query']['bool']['must'].append({'term': {'creator': indata.get('email')}})
        
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
                doc_type="forum_topic",
                size = 0,
                body = query
            )
        
        for bucket in res['aggregations']['commits']['buckets']:
            ts = int(bucket['key'] / 1000)
            count = bucket['doc_count']
            timeseries[ts] = timeseries.get(ts, makeTS(distinct))
            timeseries[ts][iType + ' topics'] = timeseries[ts].get(iType + ' topics', 0) + count
            
        
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
                                        'type': iValues
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
            query['query']['bool']['must'].append({'term': {'creator': indata.get('email')}})
        
        # Get number of closed ones, this period
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
                doc_type="forum_post",
                size = 0,
                body = query
            )
        
        for bucket in res['aggregations']['commits']['buckets']:
            ts = int(bucket['key'] / 1000)
            count = bucket['doc_count']
            timeseries[ts] = timeseries.get(ts, makeTS(distinct))
            timeseries[ts][iType + ' replies'] = timeseries[ts].get(iType + ' replies', 0) + count
        
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

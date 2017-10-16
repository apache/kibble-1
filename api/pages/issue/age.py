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
# OPENAPI-URI: /api/issue/age
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
#   summary: Shows timeseries of no. of open tickets by age
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
#   summary: Shows timeseries of no. of open tickets by age
# 
########################################################################





"""
This is the issue actors stats page for Kibble
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
    
    
    interval = indata.get('interval', 'month')
    
    ####################################################################
    ####################################################################
    dOrg = session.user['defaultOrganisation'] or "apache"
    query = {
                'query': {
                    'bool': {
                        'must': [
                            {
                                'term': {
                                    'status': 'open'
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
    if indata.get('email'):
        query['query']['bool']['should'] = [{'term': {'issueCreator': indata.get('email')}}, {'term': {'issueCloser': indata.get('email')}}]
        query['query']['bool']['minimum_should_match'] = 1
    
    # Get timeseries for this period
    query['aggs'] = {
            'per_interval': {
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
    timeseries = []
    opened = 0
    for bucket in res['aggregations']['per_interval']['buckets']:
        ts = int(bucket['key'] / 1000)
        opened += bucket['doc_count']
        timeseries.append( {
            'date': ts,
            'open': opened
        })
        
    
        
    JSON_OUT = {
        'timeseries': timeseries,
        'okay': True,
        'responseTime': time.time() - now,
        'widgetType': {
            'chartType': 'line'
        }
    }
    yield json.dumps(JSON_OUT)

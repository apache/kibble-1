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
# OPENAPI-URI: /api/mail/timeseries
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
#   summary: Shows email sent over time
# 
########################################################################





"""
This is the email timeseries renderer for Kibble
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
    
    
    dateTo = indata.get('to', int(time.time()))
    dateFrom = indata.get('from', dateTo - (86400*30*6)) # Default to a 6 month span
    
    which = 'committer_email'
    role = 'committer'
    if indata.get('author', False):
        which = 'author_email'
        role = 'author'
    
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
                                    'date': {
                                        'from': time.strftime("%Y/%m/%d 00:00:00", time.gmtime(dateFrom)),
                                        'to': time.strftime("%Y/%m/%d 23:59:59", time.gmtime(dateTo))
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
    if indata.get('email'):
        query['query']['bool']['should'] = [{'term': {'sender': indata.get('email')}}]
        query['query']['bool']['minimum_should_match'] = 1
    
    # Get number of committers, this period
    query['aggs'] = {
            'timeseries': {
                'date_histogram': {
                    'field': 'date',
                    'interval': interval
                },
                'aggs': {
                    'email': {
                        'sum': {
                            'field': 'emails'
                        }
                    },
                    'topics': {
                        'sum': {
                            'field': 'topics'
                        }
                    },
                    'authors': {
                        'sum': {
                            'field': 'authors'
                        }
                    }
                }
            }
        }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="mailstats",
            size = 0,
            body = query
        )
    
    timeseries = []
    for bucket in res['aggregations']['timeseries']['buckets']:
        ts = int(bucket['key'] / 1000)
        timeseries.append({
            'date': ts,
            'emails': bucket['email']['value'],
            'topics': bucket['topics']['value'],
            'authors': bucket['authors']['value']
        })
    
    JSON_OUT = {
        'widgetType': {
            'chartType': 'bar'  # Recommendation for the UI
        },
        'timeseries': timeseries,
        'interval': interval,
        'okay': True,
        'responseTime': time.time() - now
    }
    yield json.dumps(JSON_OUT)

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
# OPENAPI-URI: /api/mail/mood-timeseries
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
#   summary: Shows a breakdown of the (analyzed) mood in emails as a timeseries
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
#   summary: Shows a breakdown of the (analyzed) mood in emails as a timeseries
# 
########################################################################





"""
This is the email mood timeseries renderer for Kibble
"""

import json
import time

def run(API, environ, indata, session):
    
    # We need to be logged in for this!
    if not session.user:
        raise API.exception(403, "You must be logged in to use this API endpoint! %s")
    
    
    # First, fetch the view if we have such a thing enabled
    viewList = []
    if indata.get('view'):
        viewList = session.getView(indata.get('view'))
    if indata.get('subfilter'):
        viewList = session.subFilter(indata.get('subfilter'), view = viewList) 
    
    dateTo = indata.get('to', int(time.time()))
    dateFrom = indata.get('from', dateTo - (86400*30*6)) # Default to a 6 month span
    interval = indata.get('interval', 'week')
    
    # Define moods we know of
    moods_good = set(['trust', 'joy', 'confident', 'positive'])
    moods_bad = set(['sadness', 'anger', 'disgust', 'fear', 'negative'])
    moods_neutral = set(['anticipation', 'surprise', 'tentative', 'analytical', 'neutral'])
    all_moods = set(moods_good | moods_bad | moods_neutral)
    
    # Fetch all sources for default org
    dOrg = session.user['defaultOrganisation'] or "apache"
    query = {
                'query': {
                    'bool': {
                        'must': [
                            {'range':
                                {
                                    'ts': {
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
                            { 'exists': {
                                'field': 'mood'
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
    
    emls = session.DB.ES.count(
            index=session.DB.dbname,
            doc_type="email",
            body = query
        )['count']
    
    query['aggs'] = {
         'history': {
            'date_histogram': {
                'field': 'date',
                'interval': interval
            },
            'aggs': {
            }
         }
    }
    
    # Add aggregations for moods
    for mood in all_moods:
        query['aggs']['history']['aggs'][mood] = {
                    'sum': {
                        'field': "mood.%s" % mood
                    }                
                }
    
    
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="email",
            size = 0,
            body = query
        )
    
    timeseries = []
    
    
    for tz in res['aggregations']['history']['buckets']:
        moods = {}
        emls = tz['doc_count']
        for mood in all_moods:
            moods[mood] = int (100 * tz.get(mood, {'value':0})['value'] / max(1, emls))
        moods['date'] = int(tz['key']/1000)
        timeseries.append(moods)
    
    JSON_OUT = {
        'timeseries': timeseries,
        'okay': True
    }
    yield json.dumps(JSON_OUT)

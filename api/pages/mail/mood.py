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
# OPENAPI-URI: /api/mail/mood
########################################################################
# get:
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Sloc'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Shows a breakdown of the (analyzed) mood in emails
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
#             $ref: '#/components/schemas/Sloc'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Shows a breakdown of the (analyzed) mood in emails
# 
########################################################################





"""
This is the email mood renderer for Kibble
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
    
    # Define moods we know of
    moods_good = set(['trust', 'joy', 'confident', 'positive'])
    moods_bad = set(['sadness', 'anger', 'disgust', 'fear', 'negative'])
    moods_neutral = set(['anticipation', 'surprise', 'tentative', 'analytical', 'neutral'])
    all_moods = set(moods_good | moods_bad | moods_neutral)
    
    # Start off with a query for the entire org (we want to compare)
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
    
    # Count all emails, for averaging scores
    gemls = session.DB.ES.count(
            index=session.DB.dbname,
            doc_type="email",
            body = query
        )['count']
    
    # Add aggregations for moods
    query['aggs'] = {
                
    }
    for mood in all_moods:
        query['aggs'][mood] = {
                    'sum': {
                        'field': "mood.%s" % mood
                    }                
                }
    
    
    global_mood_compiled = {}
    mood_compiled = {}
    txt = "This chart shows the ten potential mood types as they average on the emails in this period. A score of 100 means a sentiment is highly visible in most emails."
    gtxt = "This shows the overall estimated mood as a gauge from terrible to good."
    # If we're comparing against all lists, first do a global query
    # and compile moods overall
    if indata.get('relative'):
        txt = "This chart shows the ten potential mood types on the selected lists as they compare against all mailing lists in the database. A score of 100 here means the sentiment conforms to averages across all lists."
        gtxt = "This shows the overall estimated mood compared to all lists, as a gauge from terrible to good."
        global_moods = {}
        
        gres = session.DB.ES.search(
                index=session.DB.dbname,
                doc_type="email",
                size = 0,
                body = query
            )
        for mood, el in gres['aggregations'].items():
            # If a mood is not present (iow sum is 0), remove it from the equation by setting to -1
            if el['value'] == 0:
                el['value'] == -1
            global_moods[mood] = el['value']
        for k, v in global_moods.items():
            if v >= 0:
                global_mood_compiled[k] = int( (v / max(1,gemls)) * 100)
    
    # Now, if we have a view (or not distinguishing), ...
    ss = False
    if indata.get('source'):
        query['query']['bool']['must'].append({'term': {'sourceID': indata.get('source')}})
        ss = True
    elif viewList:
        query['query']['bool']['must'].append({'terms': {'sourceID': viewList}})
        ss = True
        
    # If we have a view enabled (and distinguish), compile local view against global view
    # Else, just copy global as local
    if ss or not indata.get('relative'):
        res = session.DB.ES.search(
                    index=session.DB.dbname,
                    doc_type="email",
                    size = 0,
                    body = query
                )
        
        del query['aggs'] # we have to remove these to do a count()
        emls = session.DB.ES.count(
            index=session.DB.dbname,
            doc_type="email",
            body = query
        )['count']
        
        moods = {}
        years = 0
        
        for mood, el in res['aggregations'].items():
            if el['value'] == 0:
                el['value'] == -1
            moods[mood] = el['value']
        for k, v in moods.items():
            if v > 0:
                mood_compiled[k] = int(100 * int( ( v / max(1,emls)) * 100) / max(1, global_mood_compiled.get(k, 100)))
    else:
        mood_compiled = global_mood_compiled
    
    # If relative mode and a field is missing, assume 100 (norm)
    if indata.get('relative'):
        for M in all_moods:
            if mood_compiled.get(M, 0) == 0:
                mood_compiled[M] = 100
    
    # Compile an overall happiness level
    MAX = max(max(mood_compiled.values()),1)
    X = 100 if indata.get('relative') else 0
    bads = X
    for B in moods_bad:
        if mood_compiled.get(B) and mood_compiled[B] > X:
            bads += mood_compiled[B]
    
    happ = 50
    
    goods = X
    for B in moods_good:
        if mood_compiled.get(B) and mood_compiled[B] > X:
            goods += mood_compiled[B]
    MAX = max(MAX, bads, goods)
    if bads > 0:
        happ -= (50*bads/MAX)
    if goods > 0:
        happ += (50*goods/MAX)
    swingometer = max(0, min(100, happ))
    
    # JSON out!
    JSON_OUT = {
        'relativeMode': True,
        'text': txt,
        'counts': mood_compiled,
        'okay': True,
        'gauge': {
            'key': 'Happiness',
            'value': swingometer,
            'text': gtxt
        }
    }
    yield json.dumps(JSON_OUT)

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
                'joy': {
                    'sum': {
                        'field': 'mood.joy'
                    }                
                },
                'sadness': {
                    'sum': {
                        'field': 'mood.sadness'
                    }                
                },
                'tentative': {
                    'sum': {
                        'field': 'mood.tentative'
                    }                
                },
                'confident': {
                    'sum': {
                        'field': 'mood.confident'
                    }                
                },
                'anger': {
                    'sum': {
                        'field': 'mood.anger'
                    }                
                },
                'fear': {
                    'sum': {
                        'field': 'mood.fear'
                    }                
                },
                'analytical': {
                    'sum': {
                        'field': 'mood.analytical'
                    }                
                }
    }
    
    
    global_mood_compiled = {}
    mood_compiled = {}
    txt = "This chart shows the seven mood types as they average on the emails in this period. A score of 100 means a sentiment is highly visible in most emails."
    gtxt = "This shows the overall estimated mood as a gauage from terrible to good."
    # If we're comparing against all lists, first do a global query
    # and compile moods overall
    if indata.get('relative'):
        txt = "This chart shows the seven mood types on the selected lists as they compare against all mailing lists in the database. A score of 100 here means the sentiment conforms to averages across all lists."
        gtxt = "This shows the overall estimated mood copmpared to all lists, as a gauage from terrible to good."
        global_moods = {}
        
        gres = session.DB.ES.search(
                index=session.DB.dbname,
                doc_type="email",
                size = 0,
                body = query
            )
        for mood, el in gres['aggregations'].items():
            global_moods[mood] = el['value']
        for k, v in global_moods.items():
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
    if ss or not indata.get('distinguish'):
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
            moods[mood] = el['value']
        for k, v in moods.items():
            mood_compiled[k] = int(100 * int( (v / max(1,emls)) * 100) / max(1, global_mood_compiled.get(k, 100)))
    else:
        mood_compiled = global_mood_compiled
    MAX = max(mood_compiled.values())
    bads = (mood_compiled.get('anger', 0)*1.25 + mood_compiled.get('fear', 0)*1.25 + mood_compiled.get('sadness', 0) + mood_compiled.get('disgust', 0)*1.5) / 4
    neutrals = (mood_compiled.get('tentative', 0) + mood_compiled.get('analytical', 0) /2)
    goods = (mood_compiled.get('joy', 0)*1.5 + mood_compiled.get('confident', 0)) / 2
    swingometer = max(0, min(100, (50 + goods - bads) / max(1, (MAX/100))))
    
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

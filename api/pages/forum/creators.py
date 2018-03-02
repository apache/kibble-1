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
# OPENAPI-URI: /api/forum/creators
########################################################################
# get:
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/CommitterList'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Shows the top N of issue openers
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
#             $ref: '#/components/schemas/CommitterList'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Shows the top N of forum topic creators
# 
########################################################################





"""
This is the TopN issue openers list renderer for Kibble
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
    
    interval = indata.get('interval', 'month')
    xtitle = None
    
    ####################################################################
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
        xtitle = "People opening issues solved by %s" % indata.get('email')
    
    # Get top 25 committers this period
    query['aggs'] = {
            'committers': {
                'terms': {
                    'field': 'creator',
                    'size': 25
                },
                'aggs': {
                
            }
        }        
    }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="forum_topic",
            size = 0,
            body = query
        )

    people = {}
    for bucket in res['aggregations']['committers']['buckets']:
        email = bucket['key']
        count = bucket['doc_count']
        sha = email
        if session.DB.ES.exists(index=session.DB.dbname,doc_type="person",id = sha):
            pres = session.DB.ES.get(
                index=session.DB.dbname,
                doc_type="person",
                id = email
                )
            person = pres['_source']
            person['name'] = person.get('name', 'unknown')
            people[email] = person
            people[email]['gravatar'] = hashlib.md5(person.get('email', 'unknown').encode('utf-8')).hexdigest()
            people[email]['count'] = count
        
    topN = []
    for email, person in people.items():
        topN.append(person)
    topN = sorted(topN, key = lambda x: x['count'], reverse = True)
    JSON_OUT = {
        'topN': {
            'denoter': 'topics created',
            'items': topN,
        },
        'okay': True,
        'responseTime': time.time() - now,
        'widgetType': {
            'chartType': 'bar',
            'title': xtitle
        }
    }
    yield json.dumps(JSON_OUT)

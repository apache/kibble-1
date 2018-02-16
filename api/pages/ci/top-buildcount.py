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
# OPENAPI-URI: /api/ci/top-buildcount
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
#   summary: Shows top 25 repos by lines of code
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
#   summary: Shows top 25 jobs by total builds done. Essentially buildtime, tweaked
# 
########################################################################





"""
This is the TopN CI jobs by total build time renderer for Kibble
"""

import json
import time
import re

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
                                        'from': time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(dateFrom)),
                                        'to': time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(dateTo))
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
    
    query['aggs'] = {
        'by_job': {
                'terms': {
                    'field': 'jobURL.keyword',
                    'size': 5000,
                },
                'aggs': {
                    'duration': {
                        'sum': {
                            'field': 'duration'
                        }
                    },
                    'ci': {
                        'terms': {
                            'field': 'ci.keyword',
                            'size': 1
                        }
                    },
                    'name': {
                        'terms': {
                            'field': 'job.keyword',
                            'size': 1
                        }
                    }
                }
            }
        }
    
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="ci_build",
            size = 0,
            body = query
        )
    
    jobs = []
    for doc in res['aggregations']['by_job']['buckets']:
        job = doc['key']
        builds = doc['doc_count']
        duration = doc['duration']['value']
        ci = doc['ci']['buckets'][0]['key']
        jobname = doc['name']['buckets'][0]['key']
        jobs.append([builds, duration, jobname, ci])
    
    topjobs = sorted(jobs, key = lambda x: int(x[0]), reverse = True)
    tophash = {}
    for v in topjobs:
        tophash["%s (%s)" % (v[2], v[3])] = v[0]
        
    JSON_OUT = {
        'counts': tophash,
        'okay': True,
        'responseTime': time.time() - now,
    }
    yield json.dumps(JSON_OUT)

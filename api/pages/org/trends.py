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
# OPENAPI-URI: /api/org/trends
########################################################################
# get:
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Trend'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Shows a quick trend summary of the past 6 months for your org
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
#   summary: Shows a quick trend summary of the past 6 months for your org
# 
########################################################################





"""
This is the org trend renderer for Kibble
"""

import json
import time

def run(API, environ, indata, session):
    
    # We need to be logged in for this!
    if not session.user:
        raise API.exception(403, "You must be logged in to use this API endpoint! %s")
    
    now = time.time()
    
    # First, fetch the view if we have such a thing enabled
    viewList = []
    if indata.get('view'):
        if session.DB.ES.exists(index=session.DB.dbname, doc_type="view", id = indata['view']):
            view = session.DB.ES.get(index=session.DB.dbname, doc_type="view", id = indata['view'])
            viewList = view['_source']['sourceList']
    
    dateTo = int(time.time())
    dateFrom = dateTo - (86400*30*3) # Default to a quarter
    if dateFrom < 0:
        dateFrom = 0
    dateYonder = dateFrom - (dateTo - dateFrom)
    
    
    
    ####################################################################
    # We start by doing all the queries for THIS period.               #
    # Then we reset the query, and change date to yonder-->from        #
    # and rerun the same queries.                                      #
    ####################################################################
    dOrg = session.user['defaultOrganisation'] or "kibbledemo"
    query = {
                'query': {
                    'bool': {
                        'must': [
                            {'range':
                                {
                                    'tsday': {
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
    
    # Get number of commits, this period
    res = session.DB.ES.count(
            index=session.DB.dbname,
            doc_type="code_commit",
            body = query
        )
    no_commits = res['count']
    
    
    # Get number of committers, this period
    query['aggs'] = {
            'authors': {
                'cardinality': {
                    'field': 'author_email'
                }
            }
            
        }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="code_commit",
            size = 0,
            body = query
        )
    no_authors = res['aggregations']['authors']['value']
    
    
    ####################################################################
    # Change to PRIOR SPAN                                             #
    ####################################################################
    dOrg = session.user['defaultOrganisation'] or "apache"
    query = {
                'query': {
                    'bool': {
                        'must': [
                            {'range':
                                {
                                    'tsday': {
                                        'from': dateYonder,
                                        'to': dateFrom-1
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
    
    # Get number of commits, this period
    res = session.DB.ES.count(
            index=session.DB.dbname,
            doc_type="code_commit",
            body = query
        )
    no_commits_before = res['count']
    
    # Get number of committers, this period
    query['aggs'] = {
            'authors': {
                'cardinality': {
                    'field': 'author_email'
                }
            }
        }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="code_commit",
            size = 0,
            body = query
        )
    no_authors_before = res['aggregations']['authors']['value']
    
    
    trends = {
        "authors": {
            'before': no_authors_before,
            'after': no_authors,
            'title': "Contributors this quarter"
        },
        'commits': {
            'before': no_commits_before,
            'after': no_commits,
            'title': "Commits this quarter"
        }
    }
    
    JSON_OUT = {
        'trends': trends,
        'okay': True,
        'responseTime': time.time() - now
    }
    yield json.dumps(JSON_OUT)

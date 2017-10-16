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
# OPENAPI-URI: /api/bio/trends
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
#   summary: Shows a quick trend summary of the past 6 months for a contributor
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
#   summary: Shows a quick trend summary of the past 6 months for a contributor
# 
########################################################################





"""
This is the contributor trends renderer for Kibble
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
        viewList = session.getView(indata.get('view'))
    if indata.get('subfilter'):
        viewList = session.subFilter(indata.get('subfilter'), view = viewList) 
    
    
    dateTo = indata.get('to', int(time.time()))
    dateFrom = indata.get('from', dateTo - (86400*30*6)) # Default to a 6 month span
    if dateFrom < 0:
        dateFrom = 0
    dateYonder = dateFrom - (dateTo - dateFrom)
    
    
    dOrg = session.user['defaultOrganisation'] or "apache"
    
    ####################################################################
    # We start by doing all the queries for THIS period.               #
    # Then we reset the query, and change date to yonder-->from        #
    # and rerun the same queries.                                      #
    ####################################################################
    
    rangeKey = 'created'
    rangeQuery = {'range':
                    {
                        rangeKey: {
                            'from': dateFrom,
                            'to': dateTo
                        }
                    }
                }
    # ISSUES OPENED
    query = {
                'query': {
                    'bool': {
                        'must': [
                            rangeQuery,
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
        codeKey = 'committer_email' if not indata.get('author') else 'author_email'
        query['query']['bool']['should'] = [
            {'term': {'issueCreator': indata.get('email')}},
            {'term': {'issueCloser': indata.get('email')}},
            {'term': {'sender': indata.get('email')}},
            {'term': {codeKey: indata.get('email')}},
        ]
        query['query']['bool']['minimum_should_match'] = 1
    
    
    # ISSUES CREATED
    res = session.DB.ES.count(
            index=session.DB.dbname,
            doc_type="issue",
            body = query
        )
    no_issues_created = res['count']
    
    
    # ISSUES CLOSED
    rangeKey = "closed"
    query['query']['bool']['must'][0] = {'range':
                    {
                        rangeKey: {
                            'from': dateFrom,
                            'to': dateTo
                        }
                    }
                }
    
    res = session.DB.ES.count(
            index=session.DB.dbname,
            doc_type="issue",
            body = query
        )
    no_issues_closed = res['count']
    
    
    # EMAIL SENT
    rangeKey = "ts"
    query['query']['bool']['must'][0] = {'range':
                    {
                        rangeKey: {
                            'from': dateFrom,
                            'to': dateTo
                        }
                    }
                }
    
    res = session.DB.ES.count(
            index=session.DB.dbname,
            doc_type="email",
            body = query
        )
    no_email_sent = res['count']
    
    # COMMITS MADE
    rangeKey = "ts"
    query['query']['bool']['must'][0] = {'range':
                    {
                        rangeKey: {
                            'from': dateFrom,
                            'to': dateTo
                        }
                    }
                }
    
    res = session.DB.ES.count(
            index=session.DB.dbname,
            doc_type="code_commit",
            body = query
        )
    no_commits = res['count']
    
    
    
    ####################################################################
    # Change to PRIOR SPAN                                             #
    ####################################################################
    
    # ISSUES OPENED
    rangeKey = "created"
    query['query']['bool']['must'][0] = {'range':
                    {
                        rangeKey: {
                            'from': dateYonder,
                            'to': dateFrom-1
                        }
                    }
                }
    
    res = session.DB.ES.count(
            index=session.DB.dbname,
            doc_type="issue",
            body = query
        )
    no_issues_created_before = res['count']
    
    
    
    # ISSUES CLOSED
    rangeKey = "closed"
    query['query']['bool']['must'][0] = {'range':
                    {
                        rangeKey: {
                            'from': dateYonder,
                            'to': dateFrom-1
                        }
                    }
                }
    
    res = session.DB.ES.count(
            index=session.DB.dbname,
            doc_type="issue",
            body = query
        )
    no_issues_closed_before = res['count']
    
    
    # EMAIL SENT
    rangeKey = "ts"
    query['query']['bool']['must'][0] = {'range':
                    {
                        rangeKey: {
                            'from': dateYonder,
                            'to': dateFrom-1
                        }
                    }
                }
    
    
    res = session.DB.ES.count(
            index=session.DB.dbname,
            doc_type="email",
            body = query
        )
    no_email_sent_before = res['count']
    
    # CODE COMMITS
    rangeKey = "ts"
    query['query']['bool']['must'][0] = {'range':
                    {
                        rangeKey: {
                            'from': dateYonder,
                            'to': dateFrom-1
                        }
                    }
                }
    
    
    res = session.DB.ES.count(
            index=session.DB.dbname,
            doc_type="code_commit",
            body = query
        )
    no_commits_before = res['count']
    
    
    trends = {
        "created": {
            'before': no_issues_created_before,
            'after': no_issues_created,
            'title': "Issues opened this period"
        },
        "closed": {
            'before': no_issues_closed_before,
            'after': no_issues_closed,
            'title': "Issues closed this period"
        },
        "email": {
            'before': no_email_sent_before,
            'after': no_email_sent,
            'title': "Emails sent this period"
        },
        "code": {
            'before': no_commits_before,
            'after': no_commits,
            'title': "Commits this period"
        }
    }
    
    JSON_OUT = {
        'trends': trends,
        'okay': True,
        'responseTime': time.time() - now
    }
    yield json.dumps(JSON_OUT)

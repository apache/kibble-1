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
# OPENAPI-URI: /api/code/activity
########################################################################
# get:
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Factor'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Shows community activity data for a set of repos over a given period of time
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
#             $ref: '#/components/schemas/Factor'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Shows community activity data for a set of repos over a given period of time
# 
########################################################################





"""
This is the community activity renderer for Kibble
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
    if dateFrom < 0:
        dateFrom = 0
    dateYonder = dateFrom - (dateTo - dateFrom)
    

    ####################################################################
    # COMMITS                                                          #
    ####################################################################
    dOrg = session.user['defaultOrganisation'] or "apache"
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
    # Source-specific or view-specific??
    if indata.get('source'):
        query['query']['bool']['must'].append({'term': {'sourceID': indata.get('source')}})
    elif viewList:
        query['query']['bool']['must'].append({'terms': {'sourceID': viewList}})
    if indata.get('email'):
        query['query']['bool']['should'] = [{'term': {'committer_email': indata.get('email')}}, {'term': {'author_email': indata.get('email')}}]
        query['query']['bool']['minimum_should_match'] = 1
    
    # Get number of commits, this period
    res = session.DB.ES.count(
            index=session.DB.dbname,
            doc_type="code_commit",
            body = query
        )
    no_commits = res['count']



    ####################################################################
    # ISSUES OPENED                                                    #
    ####################################################################
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
        query['query']['bool']['should'] = [{'term': {'issueCreator': indata.get('email')}}, {'term': {'issueCloser': indata.get('email')}}]
        query['query']['bool']['minimum_should_match'] = 1
    
    # Get number of issues created, this period
    res = session.DB.ES.count(
            index=session.DB.dbname,
            doc_type="issue",
            body = query
        )
    no_issues_created = res['count']

    
    ####################################################################
    # COMMENTS                                                         #
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
                },
                'sort': {
                    'comments': 'desc'
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
    
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="issue",
            size = 25,
            body = query
        )

    no_comments = 0;
    for bucket in res['hits']['hits']:
        doc = bucket['_source']
        doc['count'] = doc.get('comments', 0)
        no_comments += doc['count']


    
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
    # Source-specific or view-specific??
    if indata.get('source'):
        query['query']['bool']['must'].append({'term': {'sourceID': indata.get('source')}})
    elif viewList:
        query['query']['bool']['must'].append({'terms': {'sourceID': viewList}})
    if indata.get('email'):
        query['query']['bool']['should'] = [{'term': {'committer_email': indata.get('email')}}, {'term': {'author_email': indata.get('email')}}]
        query['query']['bool']['minimum_should_match'] = 1
    
    # Get number of commits, this period
    res = session.DB.ES.count(
            index=session.DB.dbname,
            doc_type="code_commit",
            body = query
        )
    no_commits_b = res['count']


    ####################################################################
    ####################################################################
    query = {
                'query': {
                    'bool': {
                        'must': [
                            {'range':
                                {
                                    'created': {
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
    # Source-specific or view-specific??
    if indata.get('source'):
        query['query']['bool']['must'].append({'term': {'sourceID': indata.get('source')}})
    elif viewList:
        query['query']['bool']['must'].append({'terms': {'sourceID': viewList}})
    if indata.get('email'):
        query['query']['bool']['should'] = [{'term': {'issueCreator': indata.get('email')}}, {'term': {'issueCloser': indata.get('email')}}]
        query['query']['bool']['minimum_should_match'] = 1
    
    # Get number of issues created, this period
    res = session.DB.ES.count(
            index=session.DB.dbname,
            doc_type="issue",
            body = query
        )
    no_issues_created_b = res['count']


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
                },
                'sort': {
                    'comments': 'desc'
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
    
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="issue",
            size = 25,
            body = query
        )

    no_comments_b = 0;
    for bucket in res['hits']['hits']:
        doc = bucket['_source']
        doc['count'] = doc.get('comments', 0)
        no_comments_b += doc['count']



    total = no_commits + no_issues_created + no_comments
    total_b = no_commits_b + no_issues_created_b + no_comments_b

    JSON_OUT = {
        'factors': [
            {
                'title': "Commits",
                'count': no_commits,
                'previous': no_commits_b
            },
            {
                'title': "Issues",
                'count': no_issues_created,
                'previous': no_issues_created_b
            },
            {
                'title': "Comments",
                'count': no_comments,
                'previous': no_comments_b
            },
            {
                'title': "Total Activity",
                'count': total,
                'previous': total_b
            }
        ],
        'okay': True,
        'responseTime': time.time() - now,
    }
    yield json.dumps(JSON_OUT)

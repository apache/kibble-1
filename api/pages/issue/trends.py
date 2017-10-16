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
# OPENAPI-URI: /api/issue/trends
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
#   summary: Shows trend data for a set of issue trackers over a given period of time
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
#   summary: Shows trend data for a set of issue trackers over a given period of time
# 
########################################################################





"""
This is the Issue trends renderer for Kibble
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
    
    
    # Get number of open/close, this period
    query['aggs'] = {
            'opener': {
                'cardinality': {
                    'field': 'issueCreator'
                }
            }
        }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="issue",
            size = 0,
            body = query
        )
    no_creators = res['aggregations']['opener']['value']
    
    
    # CLOSERS
    
    query = {
                'query': {
                    'bool': {
                        'must': [
                            {'range':
                                {
                                    'closed': {
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
    no_issues_closed = res['count']
    
    
    # Get number of open/close, this period
    query['aggs'] = {
            'closer': {
                'cardinality': {
                    'field': 'issueCloser'
                }
            }
        }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="issue",
            size = 0,
            body = query
        )
    no_closers = res['aggregations']['closer']['value']
    
    
    
    ####################################################################
    # Change to PRIOR SPAN                                             #
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
    if viewList:
        query['query']['bool']['must'].append({'terms': {'sourceID': viewList}})
    if indata.get('email'):
        query['query']['bool']['should'] = [{'term': {'issueCreator': indata.get('email')}}, {'term': {'issueCloser': indata.get('email')}}]
        query['query']['bool']['minimum_should_match'] = 1
    
    # Get number of issues, this period
    res = session.DB.ES.count(
            index=session.DB.dbname,
            doc_type="issue",
            body = query
        )
    no_issues_created_before = res['count']
    
    # Get number of committers, this period
    query['aggs'] = {
            'opener': {
                'cardinality': {
                    'field': 'issueCreator'
                }
            }
        }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="issue",
            size = 0,
            body = query
        )
    no_creators_before = res['aggregations']['opener']['value']
    
    
    
    # CLOSERS
    
    query = {
                'query': {
                    'bool': {
                        'must': [
                            {'range':
                                {
                                    'closed': {
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
    if viewList:
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
    no_issues_closed_before = res['count']
    
    
    # Get number of open/close, this period
    query['aggs'] = {
            'closer': {
                'cardinality': {
                    'field': 'issueCloser'
                }
            }
        }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="issue",
            size = 0,
            body = query
        )
    no_closers_before = res['aggregations']['closer']['value']
    
    
    trends = {
        "created": {
            'before': no_issues_created_before,
            'after': no_issues_created,
            'title': "Issues opened this period"
        },
        "authors": {
            'before': no_creators_before,
            'after': no_creators,
            'title': "People opening issues this period"
        },
        "closed": {
            'before': no_issues_closed_before,
            'after': no_issues_closed,
            'title': "Issues closed this period"
        },
        "closers": {
            'before': no_closers_before,
            'after': no_closers,
            'title': "People closing issues this period"
        }
    }
    
    JSON_OUT = {
        'trends': trends,
        'okay': True,
        'responseTime': time.time() - now
    }
    yield json.dumps(JSON_OUT)

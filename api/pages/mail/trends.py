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
# OPENAPI-URI: /api/mail/trends
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
#   summary: Shows a quick email trend summary of the past 6 months for your org
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
#   summary: Shows a quick email trend summary of the past 6 months for your org
# 
########################################################################





"""
This is the Email trends renderer for Kibble
"""

import json
import time
import datetime

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
                                    'date': {
                                        'from': time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(dateFrom)),
                                        'to': time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(dateTo))
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
        query['query']['bool']['must'].append({'term': {'sender': indata.get('email')}})
    
    
    # Get number of threads and emails, this period
    query['aggs'] = {
            'topics': {
                'sum': {
                    'field': 'topics'
                }
            },
            'emails': {
                'sum': {
                    'field': 'emails'
                }
            }
        }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="mailstats",
            size = 0,
            body = query
        )
    no_topics = res['aggregations']['topics']['value']
    no_emails = res['aggregations']['emails']['value']
    
    
    # Authors
    
    query = {
                'query': {
                    'bool': {
                        'must': [
                            {'range':
                                {
                                    'date': {
                                        'from': time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(dateFrom)),
                                        'to': time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(dateTo))
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
        query['query']['bool']['must'].append({'term': {'sender': indata.get('email')}})
    
    # Get number of authors, this period
    query['aggs'] = {
            'authors': {
                'cardinality': {
                    'field': 'sender'
                }
            }
        }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="email",
            size = 0,
            body = query
        )
    no_authors = res['aggregations']['authors']['value']
    
    
    
    ####################################################################
    # Change to PRIOR SPAN                                             #
    ####################################################################
    query = {
                'query': {
                    'bool': {
                        'must': [
                            {'range':
                                {
                                    'date': {
                                        'from': time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(dateYonder)),
                                        'to': time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(dateFrom-1))
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
        query['query']['bool']['must'].append({'term': {'sender': indata.get('email')}})
    
    
    # Get number of threads and emails, this period
    query['aggs'] = {
            'topics': {
                'sum': {
                    'field': 'topics'
                }
            },
            'emails': {
                'sum': {
                    'field': 'emails'
                }
            }
        }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="mailstats",
            size = 0,
            body = query
        )
    no_topics_before = res['aggregations']['topics']['value']
    no_emails_before = res['aggregations']['emails']['value']
    
    
    # Authors
    
    query = {
                'query': {
                    'bool': {
                        'must': [
                            {'range':
                                {
                                    'date': {
                                        'from': time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(dateYonder)),
                                        'to': time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(dateFrom-1))
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
        query['query']['bool']['must'].append({'term': {'sender': indata.get('email')}})
    
    # Get number of authors, this period
    query['aggs'] = {
            'authors': {
                'cardinality': {
                    'field': 'sender'
                }
            }
        }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="email",
            size = 0,
            body = query
        )
    no_authors_before = res['aggregations']['authors']['value']
    
    
    
    
    trends = {
        "authors": {
            'before': no_authors_before,
            'after': no_authors,
            'title': "People sending email this period"
        },
        "topics": {
            'before': no_topics_before,
            'after': no_topics,
            'title': "Topics discussed this period"
        },
        "email": {
            'before': no_emails_before,
            'after': no_emails,
            'title': "Emails sent this period"
        }
    }
    
    JSON_OUT = {
        'trends': trends,
        'okay': True,
        'responseTime': time.time() - now
    }
    yield json.dumps(JSON_OUT)

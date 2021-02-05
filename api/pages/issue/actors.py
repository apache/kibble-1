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
# OPENAPI-URI: /api/issue/actors
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
#   summary: Shows timeseries of no. of people opening/closing issues over time
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
#   summary: Shows timeseries of no. of people opening/closing issues over time
#
########################################################################





"""
This is the issue actors stats page for Kibble
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


    ####################################################################
    ####################################################################
    dOrg = session.user['defaultOrganisation'] or "apache"
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

    # Get timeseries for this period
    query['aggs'] = {
            'per_interval': {
                'date_histogram': {
                    'field': 'closedDate',
                    'interval': interval
                },
                'aggs': {
                    'by_user': {
                        'cardinality': {
                            'field': 'issueCloser'
                        }
                    }
                }
            }
        }

    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="issue",
            size = 0,
            body = query
        )

    timeseries = {}
    for bucket in res['aggregations']['per_interval']['buckets']:
        ts = int(bucket['key'] / 1000)
        ccount = bucket['by_user']['value']
        timeseries[ts] = {
            'date': ts,
            'closers': ccount,
            'openers': 0
        }


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
        query['query']['bool']['should'] = [{'term': {'issueCreator': indata.get('email')}}, {'term': {'issueCloser': indata.get('email')}}]
        query['query']['bool']['minimum_should_match'] = 1

    # Get timeseries for this period
    query['aggs'] = {
            'per_interval': {
                'date_histogram': {
                    'field': 'createdDate',
                    'interval': interval
                },
                'aggs': {
                    'by_user': {
                        'cardinality': {
                            'field': 'issueCreator'
                        }
                    }
                }
            }
        }

    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="issue",
            size = 0,
            body = query
        )

    for bucket in res['aggregations']['per_interval']['buckets']:
        ts = int(bucket['key'] / 1000)
        ccount = bucket['by_user']['value']
        if ts in timeseries:
            timeseries[ts]['openers'] = ccount
        else:
            timeseries[ts] = {
                'date': ts,
                'closers': 0,
                'openers': ccount
            }

    ts = []
    for x, el in timeseries.items():
        ts.append(el)

    JSON_OUT = {
        'timeseries': ts,
        'okay': True,
        'responseTime': time.time() - now,
        'widgetType': {
            'chartType': 'bar'
        }
    }
    yield json.dumps(JSON_OUT)

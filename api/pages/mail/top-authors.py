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
# OPENAPI-URI: /api/mail/top-authors
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
#   summary: Shows the top N of email authors
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
#   summary: Shows the top N of email authors
#
########################################################################





"""
This is the TopN committers list renderer for Kibble
"""

import json
import time
import hashlib
import re

ROBITS = r"(git|jira|jenkins|gerrit)@"

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

    # Get top 25 committers this period
    query['aggs'] = {
            'authors': {
                'terms': {
                    'field': 'sender',
                    'size': 30
                }
            }
        }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="email",
            size = 0,
            body = query
        )

    people = {}
    for bucket in res['aggregations']['authors']['buckets']:
        email = bucket['key']
        # By default, we want to see humans, not bots on this list!
        if re.match(ROBITS, email):
            continue
        count = bucket['doc_count']
        sha = hashlib.sha1( ("%s%s" % (dOrg, email)).encode('utf-8') ).hexdigest()
        if session.DB.ES.exists(index=session.DB.dbname,doc_type="person",id = sha):
            pres = session.DB.ES.get(
                index=session.DB.dbname,
                doc_type="person",
                id = sha
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
            'denoter': 'emails',
            'items': topN
        },
        'sorted': people,
        'okay': True,
        'responseTime': time.time() - now
    }
    yield json.dumps(JSON_OUT)

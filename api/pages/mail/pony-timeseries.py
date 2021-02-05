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
# OPENAPI-URI: /api/mail/pony-timeseries
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
#   summary: Shows timeseries of Pony Factor over time
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
#   summary: Shows timeseries of Pony Factor over time
#
########################################################################





"""
This is the pony factor renderer for Kibble
"""

import json
import time
import re
import datetime
import dateutil.relativedelta

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

    hl = indata.get('span', 24)
    tnow = datetime.date.today()
    nm = tnow.month - (tnow.month % 3)
    ny = tnow.year
    ts = []

    if nm < 1:
        nm += 12
        ny = ny - 1

    while ny > 1970:
        d = datetime.date(ny, nm, 1)
        t = time.mktime(d.timetuple())
        d = d - dateutil.relativedelta.relativedelta(months=hl)
        tf = time.mktime(d.timetuple())
        nm -= 3
        if nm < 1:
            nm += 12
            ny = ny - 1


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
                                            'from': tf,
                                            'to': t
                                        }
                                    }
                                },
                                {
                                    'term': {
                                        'organisation': dOrg
                                    }
                                }
                            ],
                            'must_not': [
                                {
                                    'match': {
                                        'sourceURL': 'commits*'
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

        # Get an initial count of commits
        res = session.DB.ES.count(
                index=session.DB.dbname,
                doc_type="email",
                body = query
            )

        globcount = res['count']
        if globcount == 0:
            break

        # Get top 25 committers this period
        query['aggs'] = {
                'by_sender': {
                    'terms': {
                        'field': 'sender',
                        'size': 2500
                    }
                }
            }
        res = session.DB.ES.search(
                index=session.DB.dbname,
                doc_type="email",
                size = 0,
                body = query
            )


        # PF for authors
        pf_author = 0
        pf_author_count = 0
        cpf = {}
        for bucket in res['aggregations']['by_sender']['buckets']:
            count = bucket['doc_count']
            # Assume anyone sending > 10 emails per day is a bot (or a commit list)!
            if count > (10*365*hl):
                globcount -= count
                continue
            pf_author += 1
            pf_author_count += count
            if '@' in bucket['key']:
                mldom = bucket['key'].lower().split('@')[-1]
                cpf[mldom] = True
            if pf_author_count > int(globcount/2):
                break
        ts.append({
            'date': t,
            'Pony Factor (authors)': pf_author,
            'Meta-Pony Factor': len(cpf)
        })

    ts = sorted(ts, key = lambda x: x['date'])

    JSON_OUT = {
        'text': "This shows Pony Factors as calculated over a %u month timespan. Authorship is a measure of the people it takes to make up the bulk of email traffic, and meta-pony is an estimation of how many organisations/companies are involved." % hl,
        'timeseries': ts,
        'okay': True,
        'responseTime': time.time() - now,
    }
    yield json.dumps(JSON_OUT)

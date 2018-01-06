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
# OPENAPI-URI: /api/code/pony-timeseries
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
                                        'tsday': {
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
                doc_type="code_commit",
                body = query
            )
        
        globcount = res['count']
        if globcount == 0:
            break
        
        # Get top 25 committers this period
        query['aggs'] = {
                'by_committer': {
                    'terms': {
                        'field': 'committer_email',
                        'size': 1000
                    }                
                },
                'by_author': {
                    'terms': {
                        'field': 'author_email',
                        'size': 1000
                    }                
                }
            }
        res = session.DB.ES.search(
                index=session.DB.dbname,
                doc_type="code_commit",
                size = 0,
                body = query
            )
        
        
        # PF for committers
        pf_committer = 0
        pf_committer_count = 0
        for bucket in res['aggregations']['by_committer']['buckets']:
            count = bucket['doc_count']
            pf_committer += 1
            pf_committer_count += count
            if pf_committer_count > int(globcount/2):
                break
            
        # PF for authors
        pf_author = 0
        pf_author_count = 0
        cpf = {}
        for bucket in res['aggregations']['by_author']['buckets']:
            count = bucket['doc_count']
            pf_author += 1
            pf_author_count += count
            if '@' in bucket['key']:
                mldom = bucket['key'].lower().split('@')[-1]
                cpf[mldom] = True
            if pf_author_count > int(globcount/2):
                break
        ts.append({
            'date': t,
            'Pony Factor (committership)': pf_committer,
            'Pony Factor (authorship)': pf_author,
            'Meta-Pony Factor': len(cpf)
        })
    
    ts = sorted(ts, key = lambda x: x['date'])
    
    JSON_OUT = {
        'text': "This shows Pony Factors as calculated over a %u month timespan. Authorship measures the people writing the bulk of the codebase, committership mesaures the people committing (merging) the code, and meta-pony is an estimation of how many organisations/companies are involved." % hl,
        'timeseries': ts,
        'okay': True,
        'responseTime': time.time() - now,
    }
    yield json.dumps(JSON_OUT)

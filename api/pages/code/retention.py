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
# OPENAPI-URI: /api/code/retention
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
#   summary: Shows retention metrics for a set of repos over a given period of time
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
#   summary: Shows retention metrics for a set of repos over a given period of time
# 
########################################################################





"""
This is the code contributor retention factor renderer for Kibble
"""

import json
import time
import re
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
    
    
    hl = indata.get('span', 12) # By default, we define a contributor as active if having committer in the past year
    tnow = datetime.date.today()
    nm = tnow.month - (tnow.month % 3)
    ny = tnow.year
    cy = ny
    ts = []
    
    if nm < 1:
        nm += 12
        ny = ny - 1
    
    peopleSeen = {}
    activePeople = {}
    allPeople = {}
    FoundSomething = False
    
    ny = 1970
    while ny < cy or (ny == cy and (nm+3) <= tnow.month):
        d = datetime.date(ny, nm, 1)
        t = time.mktime(d.timetuple())
        nm += 3
        if nm > 12:
            nm -= 12
            ny = ny + 1
        if ny == cy and nm > tnow.month:
            break
        d = datetime.date(ny, nm, 1)
        tf = time.mktime(d.timetuple())
        
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
                                            'from': t,
                                            'to': tf
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
        if globcount == 0 and not FoundSomething:
            continue
        FoundSomething = True
        
        # Get top 1000 committers this period
        query['aggs'] = {
                'by_committer': {
                    'terms': {
                        'field': 'committer_email',
                        'size': 25000
                    }                
                },
                'by_author': {
                    'terms': {
                        'field': 'author_email',
                        'size': 25000
                    }                
                }
            }
        res = session.DB.ES.search(
                index=session.DB.dbname,
                doc_type="code_commit",
                size = 0,
                body = query
            )
        
        
        retained = 0
        added = 0
        lost = 0
        
        thisPeriod = []
        for bucket in res['aggregations']['by_author']['buckets']:
            who = bucket['key']
            thisPeriod.append(who)
            if who not in peopleSeen:
                peopleSeen[who] = tf
                added += 1
            activePeople[who] = tf
            if who not in allPeople:
                allPeople[who] = tf
        
        prune = []
        for k, v in activePeople.items():
            if v < (t - (hl*30.45*86400)):
                prune.append(k)
                lost += 1
        
        for who in prune:
            del activePeople[who]
            del peopleSeen[who]
        retained = len(activePeople) - added
        
        ts.append({
            'date': tf,
            'People who (re)joined': added,
            'People who quit': lost,
            'People retained': retained,
            'Active people': added + retained
        })
    
    groups = [
        ['More than 5 years', (5*365*86400)+1],
        ['2 - 5 years', (2*365*86400)+1],
        ['1 - 2 years', (365*86400)],
        ['Less than a year', 1]
    ]
    
    counts = {}
    totExp = 0
    for person, age in activePeople.items():
        totExp += time.time() - allPeople[person]
        for el in sorted(groups, key = lambda x: x[1], reverse = True):
            if allPeople[person] <= time.time() - el[1]:
                counts[el[0]] = counts.get(el[0], 0) + 1
                break
    avgyr = (totExp / (86400*365)) / max(len(activePeople),1)
    
    ts = sorted(ts, key = lambda x: x['date'])
    avgm = ""
    yr = int(avgyr)
    ym = round((avgyr-yr)*12)
    if yr >= 1:
        avgm += "%u year%s" % (yr, "s" if yr != 1 else "")
    if ym > 0:
        avgm += "%s%u month%s" % (", " if yr > 0 else "", ym, "s" if ym != 1 else "")
    JSON_OUT = {
        'text': "This shows Contributor retention as calculated over a %u month timespan. The average experience of currently active people is %s." % (hl, avgm),
        'timeseries': ts,
        'counts': counts,
        'averageYears': avgyr,
        'okay': True,
        'responseTime': time.time() - now,
    }
    yield json.dumps(JSON_OUT)

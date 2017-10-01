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
        if session.DB.ES.exists(index=session.DB.dbname, doc_type="view", id = indata['view']):
            view = session.DB.ES.get(index=session.DB.dbname, doc_type="view", id = indata['view'])
            viewList = view['_source']['sourceList']
    
    hl = indata.get('span', 1) # By default, we define a contributor as active if having committer in the past year
    tnow = datetime.date.today()
    nm = tnow.month - (tnow.month % 3)
    ny = tnow.year
    cy = ny
    ts = []
    
    peopleSeen = {}
    activePeople = {}
    
    ny = 1970
    while ny < cy or (ny == cy and nm <= tnow.month):
        d = datetime.date(ny, nm, 1)
        t = time.mktime(d.timetuple())
        d = datetime.date(ny-hl, nm, 1)
        tf = time.mktime(d.timetuple())
        nm += 3
        if nm > 12:
            nm -= 12
            ny = ny + 1
        
        
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
                doc_type="issue",
                body = query
            )
        
        globcount = res['count']
        if globcount == 0:
            continue
        
        # Get top 1000 committers this period
        query['aggs'] = {
                'by_o': {
                    'terms': {
                        'field': 'issueCloser',
                        'size': 50000
                    }                
                },
                'by_c': {
                    'terms': {
                        'field': 'issueCreator',
                        'size': 50000
                    }                
                }
            }
        res = session.DB.ES.search(
                index=session.DB.dbname,
                doc_type="issue",
                size = 0,
                body = query
            )
        
        
        retained = 0
        added = 0
        lost = 0
        
        thisPeriod = []
        for bucket in res['aggregations']['by_o']['buckets']:
            who = bucket['key']
            thisPeriod.append(who)
            if who not in peopleSeen:
                peopleSeen[who] = tf
                added += 1
            if who not in activePeople:
                activePeople[who] = tf
        
        for bucket in res['aggregations']['by_c']['buckets']:
            who = bucket['key']
            thisPeriod.append(who)
            if who not in peopleSeen:
                peopleSeen[who] = tf
                added += 1
            if who not in activePeople:
                activePeople[who] = tf
        
        prune = []
        for k, v in activePeople.items():
            if v < (tf - (hl*365*86400)):
                prune.append(k)
                lost += 1
        
        for who in prune:
            del activePeople[who]
            del peopleSeen[who]
        retained = len(activePeople)
        
        ts.append({
            'date': t,
            'People who (re)joined': added,
            'People who quit': lost,
            'People retained': retained,
            'Active people': added + retained
        })
    
    ts = sorted(ts, key = lambda x: x['date'])
    
    JSON_OUT = {
        'text': "This shows Contributor retention as calculated over a %u year timespan.." % hl,
        'timeseries': ts,
        'okay': True,
        'responseTime': time.time() - now,
    }
    yield json.dumps(JSON_OUT)

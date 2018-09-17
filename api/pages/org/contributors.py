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
# OPENAPI-URI: /api/org/contributors
########################################################################
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
#             $ref: '#/components/schemas/contributorList'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Shows contributors for the entire org or matching filters.
# 
########################################################################





"""
This is the contributor list renderer for Kibble
"""

import json
import time
import hashlib

cached_people = {} # Store people we know, so we don't have to fetch them again.

def run(API, environ, indata, session):
    
    # We need to be logged in for this!
    if not session.user:
        raise API.exception(403, "You must be logged in to use this API endpoint! %s")
    
    
    # First, fetch the view if we have such a thing enabled
    viewList = []
    if indata.get('view'):
        viewList = session.getView(indata.get('view'))
    if indata.get('subfilter'):
        viewList = session.subFilter(indata.get('subfilter'), view = viewList) 
    
    
    # Fetch all contributors for the org
    dOrg = session.user['defaultOrganisation'] or "apache"
    query = {
                'query': {
                    'bool': {
                        'must': [
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
    
    # Date specific?
    dateTo = indata.get('to', int(time.time()))
    dateFrom = indata.get('from', dateTo - (86400*30*6)) # Default to a 6 month span
    query['query']['bool']['must'].append(
        {'range':
            {
                'ts': {
                    'from': dateFrom,
                    'to': dateTo
                }
            }
        }
        )
    emails = []
    contribs = {}
    
    for field in ['sender', 'author_email', 'issueCreator', 'issueCloser']:
        N = 0
        while N < 5:
            query['aggs'] = {
                'by_id': {
                    'terms': {
                        'field': field,
                        'size': 10000,
                        'include': {
                            'partition': N,
                            'num_partitions': 5
                         },
                    }                
                }
            }
            res = session.DB.ES.search(
                    index=session.DB.dbname,
                    doc_type="*,-*_code_commit,-*_file_history",
                    size = 0,
                    body = query
                )
            # Break if we've found nothing more
            #if len(res['aggregations']['by_id']['buckets']) == 0:
                #break
            # otherwise, add 'em to the pile
            for k in res['aggregations']['by_id']['buckets']:
                if k['key'] not in emails:
                    emails.append(k['key'])
                contribs[k['key']] = contribs.get(k['key'], 0) + k['doc_count']
            N += 1
            
    people = []
    for email in emails:
        pid = hashlib.sha1( ("%s%s" % (dOrg, email)).encode('ascii', errors='replace')).hexdigest()
        person = None
        if pid in cached_people:
            person = cached_people[pid]
        else:
            try:
                doc = session.DB.ES.get(index=session.DB.dbname, doc_type = 'person', id = pid)
                cached_people[pid] = {
                    'name': doc['_source']['name'],
                    'email': doc['_source']['email'],
                    'gravatar': hashlib.md5( email.encode('ascii', errors = 'replace')).hexdigest()
                }
                person = cached_people[pid]
            except:
                pass # Couldn't find 'em, booo
        if person:
            person['contributions'] = contribs.get(email, 0)
            people.append(person)
        
    JSON_OUT = {
        'people': people,
        'okay': True
    }
    yield json.dumps(JSON_OUT)

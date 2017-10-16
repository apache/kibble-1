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
# OPENAPI-URI: /api/bio/bio
########################################################################
# get:
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Biography'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Shows some facts about a contributor
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
#             $ref: '#/components/schemas/Biography'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Shows some facts about a contributor
# 
########################################################################





"""
This is the contributor trends renderer for Kibble
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
    
    
    dOrg = session.user['defaultOrganisation'] or "apache"
    
    pid = hashlib.sha1( ("%s%s" % (dOrg, indata.get('email', '???'))).encode('ascii', errors='replace')).hexdigest()
    person = {}
    if session.DB.ES.exists(index=session.DB.dbname, doc_type="person", id = pid):
        person = session.DB.ES.get(index=session.DB.dbname, doc_type="person", id = pid)['_source']
    else:
        raise API.exception(404, "No such biography!")
    
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
                },
                'size': 1,
                'sort': [{ 'ts': 'asc' }]
            }
    # Source-specific or view-specific??
    if indata.get('source'):
        query['query']['bool']['must'].append({'term': {'sourceID': indata.get('source')}})
    elif viewList:
        query['query']['bool']['must'].append({'terms': {'sourceID': viewList}})
    if indata.get('email'):
        codeKey = 'committer_email'
        query['query']['bool']['should'] = [
            {'term': {'issueCreator': indata.get('email')}},
            {'term': {'issueCloser': indata.get('email')}},
            {'term': {'sender': indata.get('email')}},
            {'term': {codeKey: indata.get('email')}},
        ]
        query['query']['bool']['minimum_should_match'] = 1
    
    
    # FIRST EMAIL
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="email",
            body = query
        )
    firstEmail = None
    if res['hits']['hits']:
        firstEmail = res['hits']['hits'][0]['_source']['ts']
        
    # FIRST COMMIT
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="code_commit",
            body = query
        )
    firstCommit = None
    if res['hits']['hits']:
        firstCommit = res['hits']['hits'][0]['_source']['ts']
        
    # FIRST AUTHORSHIP
    query['query']['bool']['should'][3] = {'term': {'author_email': indata.get('email')}}
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="code_commit",
            body = query
        )
    firstAuthor = None
    if res['hits']['hits']:
        firstAuthor = res['hits']['hits'][0]['_source']['ts']
    
    
    # COUNT EMAIL, CODE, LINES CHANGED
    del query['sort']
    del query['size']
    no_emails = session.DB.ES.count(
            index=session.DB.dbname,
            doc_type="email",
            body = query
        )['count']
    
    no_commits = session.DB.ES.count(
            index=session.DB.dbname,
            doc_type="code_commit",
            body = query
        )['count']
    
    JSON_OUT = {
        'found': True,
        'bio': {
            'organisation': dOrg,
            'name': person['name'],
            'email': person['email'],
            'id': pid,
            'gravatar': hashlib.md5(person['email'].lower().encode('utf-8')).hexdigest(),
            'firstEmail': firstEmail,
            'firstCommit': firstCommit,
            'firstAuthor': firstAuthor,
            'tags': person.get('tags', []),
            'alts': person.get('alts', []),
            'emails': no_emails,
            'commits': no_commits
        },
        'okay': True,
        'responseTime': time.time() - now
    }
    yield json.dumps(JSON_OUT)

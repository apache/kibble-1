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
# OPENAPI-URI: /api/org/list
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
#   summary: Lists the organisations you belong to (or all, if admin)
# post:
#   requestBody:
#     content:
#       application/json:
#         schema:
#           $ref: '#/components/schemas/defaultWidgetArgs'
#     description: Nothing...
#     required: true
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             type: array
#             items:
#               $ref: '#/components/schemas/Organisation'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Lists the organisations you belong to (or all, if admin)
# put:
#   requestBody:
#     content:
#       application/json:
#         schema:
#           $ref: '#/components/schemas/NewOrg'
#     required: true
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/ActionCompleted'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Create a new organisation
# 
########################################################################





"""
This is the Org list renderer for Kibble
"""

import json
import time

def run(API, environ, indata, session):
    now = time.time()
    # We need to be logged in for this!
    if not session.user:
        raise API.exception(403, "You must be logged in to use this API endpoint!")
    
    method = environ['REQUEST_METHOD']
    # Are we making a new org?
    if method == "PUT":
        if session.user['userlevel'] == "admin":
            orgname = indata.get('name', 'Foo')
            orgdesc = indata.get('desc', '')
            orgid = indata.get('id', str(int(time.time())))
            if session.DB.ES.exists(index=session.DB.dbname, doc_type='organisation', id = orgid):
                raise API.exception(403, "Organisation ID already in use!")
            
            doc = {
                'id': orgid,
                'name': orgname,
                'description': orgdesc,
                'admins': []
            }
            session.DB.ES.index(index=session.DB.dbname, doc_type='organisation', id = orgid, body = doc)
            time.sleep(1.5)
            yield json.dumps({"okay": True, "message": "Organisation created!"})
            return
        else:
            raise API.exception(403, "Only administrators can create new organisations.")
    
    ####################################################################
    orgs = []
    if session.user['userlevel'] == "admin":
        res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="organisation",
            body = {'query': { 'match_all': {}}}
        )
        for doc in res['hits']['hits']:
            orgID = doc['_source']['id']
            numDocs = session.DB.ES.count(
                index=session.DB.dbname,
                body = {'query': { 'term': {'organisation': orgID}}}
                )['count']
            numSources = session.DB.ES.count(
                index=session.DB.dbname,
                doc_type="source",
                body = {'query': { 'term': {'organisation': orgID}}}
                )['count']
            doc['_source']['sourceCount'] = numSources
            doc['_source']['docCount'] = numDocs
            orgs.append(doc['_source'])
    else:
        res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="organisation",
            body = {'query': { 'terms': {'id': session.user['organisations']}}}
        )
        for doc in res['hits']['hits']:
            orgID = doc['_source']['id']
            numDocs = session.DB.ES.count(
                index=session.DB.dbname,
                body = {'query': { 'term': {'organisation': orgID}}}
                )['count']
            numSources = session.DB.ES.count(
                index=session.DB.dbname,
                doc_type="source",
                body = {'query': { 'term': {'organisation': orgID}}}
                )['count']
            doc['_source']['sourceCount'] = numSources
            doc['_source']['docCount'] = numDocs
            orgs.append(doc['_source'])
    
    
    JSON_OUT = {
        'organisations': orgs,
        'okay': True,
        'responseTime': time.time() - now
    }
    yield json.dumps(JSON_OUT)

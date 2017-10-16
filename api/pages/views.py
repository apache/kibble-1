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
# OPENAPI-URI: /api/views
########################################################################
# delete:
#   requestBody:
#     content:
#       application/json:
#         schema:
#           $ref: '#/components/schemas/editView'
#     description: View to delete
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
#   summary: Delete a new view
# get:
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/ViewList'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Fetches a list of all views (filters) for this user
# patch:
#   requestBody:
#     content:
#       application/json:
#         schema:
#           $ref: '#/components/schemas/editView'
#     description: New source data to set
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
#   summary: Edit an existing source
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
#             $ref: '#/components/schemas/ViewList'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Fetches a list of all views (filters) for this user
# put:
#   requestBody:
#     content:
#       application/json:
#         schema:
#           $ref: '#/components/schemas/editView'
#     description: New view data to add
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
#   summary: Add a new view
# 
########################################################################





"""
This is the views (filters) list handler for Kibble
"""

import json
import re
import time
import hashlib

def run(API, environ, indata, session):
    
    # We need to be logged in for this!
    if not session.user:
        raise API.exception(403, "You must be logged in to use this API endpoint! %s")
    
    method = environ['REQUEST_METHOD']
    dOrg = session.user['defaultOrganisation'] or "apache"
    
    # Are we adding a view?
    if method == 'PUT':
        viewID = hashlib.sha224( ("%s-%s-%s" % (time.time(), session.user['email'], dOrg) ).encode('utf-8') ).hexdigest()
        sources = indata.get('sources', [])
        name = indata.get('name', "unknown view")
        public = indata.get('public', False)
        if public:
            if not (session.user['userlevel'] == 'admin' or dOrg in session.user['ownerships']):
                raise API.exception(403, "Only owners of an organisation may create public views.")
        doc = {
            'id': viewID,
            'email': session.user['email'],
            'organisation': dOrg,
            'sourceList': sources,
            'name': name,
            'created': int(time.time()),
            'publicView': public
        }
        session.DB.ES.index(index=session.DB.dbname, doc_type="view", id = viewID, body = doc)
        yield json.dumps({'okay': True, 'message': "View created"})
    
    # Are we editing (patching) a view?
    if method == 'PATCH':
        viewID = indata.get('id')
        if viewID and session.DB.ES.exists(index=session.DB.dbname, doc_type="view", id = viewID):
            doc = session.DB.ES.get(index=session.DB.dbname, doc_type="view", id = viewID)
            if session.user['userlevel'] == 'admin' or doc['_source']['email'] == session.user['email']:
                sources = indata.get('sources', [])
                doc['_source']['sourceList'] = sources
                session.DB.ES.index(index=session.DB.dbname, doc_type="view", id = viewID, body = doc['_source'])
                yield json.dumps({'okay': True, 'message': "View updated"})
            else:
                raise API.exception(403, "You don't own this view, and cannot edit it.")
        else:
            raise API.exception(404, "We couldn't find a view with this ID.")
    
    # Removing a view?
    if method == 'DELETE':
        viewID = indata.get('id')
        if viewID and session.DB.ES.exists(index=session.DB.dbname, doc_type="view", id = viewID):
            doc = session.DB.ES.get(index=session.DB.dbname, doc_type="view", id = viewID)
            if session.user['userlevel'] == 'admin' or doc['_source']['email'] == session.user['email']:
                session.DB.ES.delete(index=session.DB.dbname, doc_type="view", id = viewID)
                yield json.dumps({'okay': True, 'message': "View deleted"})
            else:
                raise API.exception(403, "You don't own this view, and cannot delete it.")
        else:
            raise API.exception(404, "We couldn't find a view with this ID.")
            
    
    if method in ['GET', 'POST']:
        # Fetch all views for default org
        
        res = session.DB.ES.search(
                index=session.DB.dbname,
                doc_type="view",
                size = 5000,
                body = {
                    'query': {
                        'term': {
                            'email': session.user['email']
                        }
                    }
                }
            )
        
        
        # Are we looking at someone elses view?
        if indata.get('view'):
            viewID = indata.get('view')
            if session.DB.ES.exists(index=session.DB.dbname, doc_type="view", id = viewID):
                blob = session.DB.ES.get(index=session.DB.dbname, doc_type="view", id = viewID)
                if blob['_source']['email'] != session.user['email'] and not blob['_source']['publicView']:
                    blob['_source']['name'] += " (shared by " +  blob['_source']['email'] + ")"
                    res['hits']['hits'].append(blob)
        sources = []
        
        # Include public views??
        if not indata.get('sources', False):
            pres = session.DB.ES.search(
                    index=session.DB.dbname,
                    doc_type="view",
                    size = 5000,
                    body = {
                        'query': {
                            'bool': {
                                'must': [
                                    {'term':
                                        {
                                            'publicView': True
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
                )
            for hit in pres['hits']['hits']:
                if hit['_source']['email'] != session.user['email']:
                    hit['_source']['name'] += " (shared view)"
                    res['hits']['hits'].append(hit)
        
        for hit in res['hits']['hits']:
            doc = hit['_source']
            if doc['organisation'] != dOrg:
                continue
            if indata.get('quick'):
                xdoc = {
                    'id': doc['id'],
                    'name': doc['name'],
                    'organisation': doc['organisation']
                    }
                sources.append(xdoc)
            else:
                sources.append(doc)
        
        allsources = []
        if indata.get('sources', False):
            res = session.DB.ES.search(
                index=session.DB.dbname,
                doc_type="source",
                size = 5000,
                body = {
                    'query': {
                        'term': {
                            'organisation': dOrg
                        }
                    }
                }
            )
            for zdoc in res['hits']['hits']:
                doc = zdoc['_source']
                xdoc = {
                    'sourceID': doc['sourceID'],
                    'type': doc['type'],
                    'sourceURL': doc['sourceURL']
                    }
                allsources.append(xdoc)
        
        JSON_OUT = {
            'views': sources,
            'sources': allsources,
            'okay': True,
            'organisation': dOrg
        }
        yield json.dumps(JSON_OUT)

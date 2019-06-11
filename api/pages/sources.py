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
# OPENAPI-URI: /api/sources
########################################################################
# delete:
#   requestBody:
#     content:
#       application/json:
#         schema:
#           $ref: '#/components/schemas/SourceID'
#     description: Source ID info
#     required: true
#   security:
#   - cookieAuth: []
#   summary: Delete an existing source
# get:
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/SourceList'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Fetches a list of all sources for this organisation
# patch:
#   requestBody:
#     content:
#       application/json:
#         schema:
#           $ref: '#/components/schemas/Source'
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
#             $ref: '#/components/schemas/SourceList'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Fetches a list of all sources for this organisation
# put:
#   requestBody:
#     content:
#       application/json:
#         schema:
#           $ref: '#/components/schemas/SourceListAdd'
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
#   summary: Add a new source
# 
########################################################################





"""
This is the source list handler for Kibble
"""

import json
import re
import time
import hashlib
import yaml

def canModifySource(session):
    """ Determine if the user can edit sources in this org """
    
    dOrg = session.user['defaultOrganisation'] or "apache"
    if session.DB.ES.exists(index=session.DB.dbname, doc_type="organisation", id= dOrg):
        xorg = session.DB.ES.get(index=session.DB.dbname, doc_type="organisation", id= dOrg)['_source']
        if session.user['email'] in xorg['admins']:
            return True
        if session.user['userlevel'] == 'admin':
            return True
    return False

def run(API, environ, indata, session):
    
    # We need to be logged in for this!
    if not session.user:
        raise API.exception(403, "You must be logged in to use this API endpoint! %s")
    
    method = environ['REQUEST_METHOD']
    dOrg = session.user['defaultOrganisation']
    
    if method in ['GET', 'POST']:
        # Fetch organisation data
        
        # Make sure we have a default/current org set
        if 'defaultOrganisation' not in session.user or not session.user['defaultOrganisation']:
            raise API.exception(400, "You must specify an organisation as default/current in order to add sources.")
        
        if session.DB.ES.exists(index=session.DB.dbname, doc_type="organisation", id= dOrg):
            org = session.DB.ES.get(index=session.DB.dbname, doc_type="organisation", id= dOrg)['_source']
            del org['admins']
        else:
            raise API.exception(404, "No such organisation, '%s'" % (dOrg or "(None)"))
        
        sourceTypes = indata.get('types', [])
        # Fetch all sources for default org
        
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
        
        # Secondly, fetch the view if we have such a thing enabled
        viewList = []
        if indata.get('view'):
            viewList = session.getView(indata.get('view'))
        if indata.get('subfilter') and indata.get('quick'):
            viewList = session.subFilter(indata.get('subfilter'), view = viewList) 
        
        
        sources = []
        for hit in res['hits']['hits']:
            doc = hit['_source']
            if viewList and not doc['sourceID'] in viewList:
                continue
            if sourceTypes and not doc['type'] in sourceTypes:
                continue
            if indata.get('quick'):
                xdoc = {
                    'sourceID': doc['sourceID'],
                    'type': doc['type'],
                    'sourceURL': doc['sourceURL']
                    }
                sources.append(xdoc)
            else:
                # Creds should be anonymous here
                if 'creds' in doc:
                    del doc['creds']
                sources.append(doc)
        
        JSON_OUT = {
            'sources': sources,
            'okay': True,
            'organisation': org
        }
        yield json.dumps(JSON_OUT)
        return
    
    # Add one or more sources
    if method == "PUT":
        if canModifySource(session):
            new = 0
            old = 0
            stypes = yaml.load(open("yaml/sourcetypes.yaml"))
            for source in indata.get('sources', []):
                sourceURL = source['sourceURL']
                sourceType = source['type']
                creds = {}
                if not sourceType in stypes:
                    raise API.exception(400, "Attempt to add unknown source type!")
                if 'optauth' in stypes[sourceType]:
                    for el in stypes[sourceType]['optauth']:
                        if el in source and len(source[el]) > 0:
                            creds[el] = source[el]
                sourceID = hashlib.sha224( ("%s-%s" % (sourceType, sourceURL)).encode('utf-8') ).hexdigest()
                
                # Make sure we have a default/current org set
                if 'defaultOrganisation' not in session.user or not session.user['defaultOrganisation']:
                    raise API.exception(400, "You must first specify an organisation as default/current in order to add sources.")
                
                doc = {
                    'organisation': dOrg,
                    'sourceURL': sourceURL,
                    'sourceID': sourceID,
                    'type': sourceType,
                    'creds': creds,
                    'steps': {}
                }
                if session.DB.ES.exists(index=session.DB.dbname, doc_type="source", id = sourceID):
                    old += 1
                else:
                    new += 1
                session.DB.ES.index(index=session.DB.dbname, doc_type="source", id = sourceID, body = doc)
            yield json.dumps({
                "message": "Sources added/updated",
                "added": new,
                "updated": old
                })
        else:
            raise API.exception(403, "You don't have permission to add sources to this organisation.")
    
    # Delete a source
    if method == "DELETE":
        if canModifySource(session):
            sourceID = indata.get('id')
            if session.DB.ES.exists(index=session.DB.dbname, doc_type="source", id = sourceID):
                # Delete all data pertainig to this source
                # For ES >= 6.x, use a glob for removing from all indices
                if session.DB.ESversion > 5:
                    session.DB.ES.delete_by_query(index=session.DB.dbname+'_*', body = {'query': {'match': {'sourceID': sourceID}}})
                else:
                # For ES <= 5.x, just remove from the main index
                    session.DB.ES.delete_by_query(index=session.DB.dbname, body = {'query': {'match': {'sourceID': sourceID}}})
                yield json.dumps({'message': "Source deleted"})
            else:
                raise API.exception(404, "No such source item")
        else:
            raise API.exception(403, "You don't have permission to delete this source.")
        
    # Edit a source
    if method == "PATCH":
        pass

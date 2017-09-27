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
This is the source list handler for Kibble
"""

import json
import re
import time

def run(API, environ, indata, session):
    
    # We need to be logged in for this!
    if not session.user:
        raise API.exception(403, "You must be logged in to use this API endpoint! %s")
    
    # Fetch organisation data
    dOrg = session.user['defaultOrganisation'] or "apache"
    if session.DB.ES.exists(index=session.DB.dbname, doc_type="org", id= dOrg):
        org = session.DB.ES.get(index=session.DB.dbname, doc_type="org", id= dOrg)['_source']
        del org['admins']
    else:
        raise API.exception(404, "No such organisation, '%s'" % dOrg)
    
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
        if session.DB.ES.exists(index=session.DB.dbname, doc_type="view", id = indata['view']):
            view = session.DB.ES.get(index=session.DB.dbname, doc_type="view", id = indata['view'])
            viewList = view['_source']['sourceList']
    
    
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
            sources.append(doc)
    
    JSON_OUT = {
        'sources': sources,
        'okay': True,
        'organisation': org
    }
    yield json.dumps(JSON_OUT)

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
    
    # Fetch all sources for default org
    dOrg = session.user['defaultOrganisation'] or "apache"
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="view",
            size = 5000,
            body = {
                'query': {
                    'term': {
                        'owner': session.user['email']
                    }
                }
            }
        )

    sources = []
    for hit in res['hits']['hits']:
        doc = hit['_source']
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
        'views': sources,
        'okay': True,
        'organisation': dOrg
    }
    yield json.dumps(JSON_OUT)

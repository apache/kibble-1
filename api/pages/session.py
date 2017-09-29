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
This is the user session handler for Kibble
"""

import json
import re
import time
import bcrypt
import hashlib

def run(API, environ, indata, session):
    
    method = environ['REQUEST_METHOD']
    
    # Logging in?
    if method == "PUT":
        u = indata['email']
        p = indata['password']
        if session.DB.ES.exists(index=session.DB.dbname, doc_type='useraccount', id = u):
            doc = session.DB.ES.get(index=session.DB.dbname, doc_type='useraccount', id = u)
            hp = doc['_source']['password']
            if bcrypt.hashpw(p.encode('utf-8'), hp.encode('utf-8')).decode('ascii') == hp:
                sessionDoc = {
                    'cid': u,
                    'id': session.cookie,
                    'timestamp': int(time.time())
                }
                session.DB.ES.index(index=session.DB.dbname, doc_type='uisession', id = session.cookie, body = sessionDoc)
                yield json.dumps({"message": "Logged in OK!"})
                return
        
        # Fall back to a 403 if username and password did not match
        raise API.exception(403, "Wrong username or password supplied!")
    
    
    # We need to be logged in for the rest of this!
    if not session.user:
        raise API.exception(403, "You must be logged in to use this API endpoint! %s")
    
    # Delete a session (log out)
    if method == "DELETE":
        session.DB.ES.delete(index=session.DB.dbname, doc_type='uisession', id = session.cookie)
        session.newCookie()
        yield json.dumps({"message": "Logged out, bye bye!"})
    
    # Display the user data for this session
    if method == "GET":
        # Run a quick search of all orgs we have.
        res = session.DB.ES.search(
                index=session.DB.dbname,
                doc_type="organisation",
                size = 100,
                body = {
                    'query': {
                        'match_all': {}
                    }
                }
            )
    
        orgs = []
        for hit in res['hits']['hits']:
            doc = hit['_source']
            orgs.append(doc)
        
        JSON_OUT = {
            'email': session.user['email'],
            'displayName': session.user['displayName'],
            'defaultOrganisation': session.user['defaultOrganisation'],
            'organisations': session.user['organisations'],
            'ownerships': session.user['ownerships'],
            'gravatar': hashlib.md5(session.user['email'].encode('utf-8')).hexdigest(),
            'userlevel': session.user['userlevel']
        }
        yield json.dumps(JSON_OUT)
        return
    
    # Finally, if we hit a method we don't know, balk!
    yield API.exception(400, "I don't know this request method!!")
    
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
This is the session library for Apache Kibble.
It handles setting/getting cookies and user prefs
"""


# Main imports
import cgi
import re
import sys
import traceback
import http.cookies
import uuid
import elasticsearch
import time

class KibbleSession(object):
    
    def getView(self, viewID):
        if self.DB.ES.exists(index=self.DB.dbname, doc_type="view", id = viewID):
            view = self.DB.ES.get(index=self.DB.dbname, doc_type="view", id = viewID)
            return view['_source']['sourceList']
        return []
    
    def subFilter(self, subfilter, view = []):
        if len(subfilter) == 0:
            return view
        dOrg = self.user['defaultOrganisation'] or "apache"
        res = self.DB.ES.search(
                index=self.DB.dbname,
                doc_type="source",
                size = 10000,
                _source_include = ['sourceURL', 'sourceID'],
                body = {
                    'query': {
                        'bool': {
                            'must': [
                                {'term': {
                                'organisation': dOrg
                                }
                            }]
                        }
                        
                    }
                }
            )
        sources = []
        for doc in res['hits']['hits']:
            sid = doc['_source']['sourceID']
            m = re.search(subfilter, doc['_source']['sourceURL'], re.IGNORECASE)
            if m and ((not view) or (sid in view)):
                sources.append(sid)
        if not sources:
            sources = ['x'] # blank return to not show eeeeverything
        return sources
    
    def subType(self, stype, view = []):
        if len(stype) == 0:
            return view
        if type(stype) is str:
            stype = [stype]
        dOrg = self.user['defaultOrganisation'] or "apache"
        res = self.DB.ES.search(
                index=self.DB.dbname,
                doc_type="source",
                size = 10000,
                _source_include = ['sourceURL', 'sourceID', 'type'],
                body = {
                    'query': {
                        'bool': {
                            'must': [
                                {'term': {
                                'organisation': dOrg
                                }
                                },
                                {'terms': {
                                'type': stype
                                }
                                }
                            ]
                        }
                        
                    }
                }
            )
        sources = []
        for doc in res['hits']['hits']:
            sid = doc['_source']['sourceID']
            m = doc['_source']['type'] in stype
            if m and ((not view) or (sid in view)):
                sources.append(sid)
        if not sources:
            sources = ['x'] # blank return to not show eeeeverything
        return sources
            
    def logout(self):
        """Log out user and wipe cookie"""
        if self.user and self.cookie:
            cookies = http.cookies.SimpleCookie()
            cookies['kibble_session'] = "null"
            self.headers.append(('Set-Cookie', cookies['kibble_session'].OutputString()))
            try:
                self.DB.ES.delete(index=self.DB.dbname, doc_type='uisession', id = self.cookie)
                self.cookie = None
                self.user = None
            except:
                pass
    def newCookie(self):
        cookie = uuid.uuid4()
        cookies = http.cookies.SimpleCookie()
        cookies['kibble_session'] = cookie
        cookies['kibble_session']['expires'] = 86400 * 365 # Expire one year from now
        self.headers.append(('Set-Cookie', cookies['kibble_session'].OutputString()))
    def __init__(self, DB, environ, config):
        """
        Loads the current user session or initiates a new session if
        none was found.
        """
        self.config = config
        self.user = None
        self.DB = DB
        self.headers = [('Content-Type', 'application/json; charset=utf-8')]
        self.cookie = None
        
        # Construct the URL we're visiting
        self.url = "%s://%s" % (environ['wsgi.url_scheme'], environ.get('HTTP_HOST', environ.get('SERVER_NAME')))
        self.url += environ.get('SCRIPT_NAME', '/')
        
        # Get Kibble cookie
        cookie = None
        cookies = None
        if 'HTTP_KIBBLE_TOKEN' in environ:
            token = environ.get('HTTP_KIBBLE_TOKEN')
            if re.match(r"^[-a-f0-9]+$", token): # Validate token, must follow UUID4 specs
                res = self.DB.ES.search(index=self.DB.dbname, doc_type='useraccount', body = {"query": { "match": { "token": token}}})
                if res['hits']['hits']:
                    self.user = res['hits']['hits'][0]['_source']
                    self.newCookie()
        else:
            if 'HTTP_COOKIE' in environ:
                cookies = http.cookies.SimpleCookie(environ['HTTP_COOKIE'])
            if cookies and 'kibble_session' in cookies:
                cookie = cookies['kibble_session'].value
                try:
                    if re.match(r"^[-a-f0-9]+$", cookie): # Validate cookie, must follow UUID4 specs
                        doc = None
                        sdoc = self.DB.ES.get(index=self.DB.dbname, doc_type='uisession', id = cookie)
                        if sdoc and 'cid' in sdoc['_source']:
                            doc = self.DB.ES.get(index=self.DB.dbname, doc_type='useraccount', id = sdoc['_source']['cid'])
                        if doc and '_source' in doc:
                            # Make sure this cookie has been used in the past 7 days, else nullify it.
                            # Further more, run an update of the session if >1 hour ago since last update.
                            age = time.time() - sdoc['_source']['timestamp']
                            if age > (7*86400):
                                self.DB.ES.delete(index=self.DB.dbname, doc_type='uisession', id = cookie)
                                sdoc['_source'] = None # Wipe it!
                                doc = None
                            elif age > 3600:
                                sdoc['_source']['timestamp'] = int(time.time()) # Update timestamp in session DB
                                self.DB.ES.update(index=self.DB.dbname, doc_type='uisession', id = cookie, body = {'doc':sdoc['_source']})
                            if doc:
                                self.user = doc['_source']
                    else:
                        cookie = None
                except Exception as err:
                    print(err)
            if not cookie:
                self.newCookie()
        self.cookie = cookie
        
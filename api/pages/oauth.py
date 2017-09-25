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
This is the oauth handler for Pony Mail
"""

import json
import cgi
import re
import json
import elasticsearch
import requests
import time

import plugins.oauthGeneric
import plugins.oauthGoogle
import plugins.oauthGithub


def run(environ, formdata, session):
    
    yield ('Content-Type', 'application/json')
    
    # Make sure we're not already logged in!
    if session.user:
            yield json.dumps({"okay": False, "msg": "Already logged in!"})
            return
    
    js= None
    
    # GitHub OAuth
    if 'oauth_token' in formdata and 'key' in formdata and formdata['key'].find("github") != -1:
        js = plugins.oauthGithub.process(formdata, session)
    
    # Google OAuth
    elif 'oauth_token' in formdata and formdata['oauth_token'].find("https://www.google") != -1 and 'code' in formdata:
        js = plugins.oauthGoogle.process(formdata, session)

    # Fallback: Classic OAuth (a'la ASF OAuth)
    elif formdata['state'] and formdata['oauth_token']:
        js = plugins.oauthGeneric.process(formdata, session)
        
    if js:
        fullname = js['fullname'] if 'fullname' in js else js['name'] if 'name' in js else js['email']
        admin = js['isMember'] if 'isMember' in js else False # FIX: Only valid if oauth_domain is autoritative
        email = js['email']
        if fullname and email:
            cid = js['uid'] if 'uid' in js else email
            if session.DB.ES.exists(index=session.DB.dbname, doc_type='account', id = cid):
                doc = session.DB.ES.get(index=session.DB.dbname, doc_type='account', id = cid)
                user = doc['_source']
                user['timestamp'] = int(time.time())
            else:
                user = {
                    'credentials': {
                        'fullname': fullname,
                        'email': email,
                        'cid': cid,
                        'altemail': []
                    },
                    'internal': {
                        'oauth_used': js['oauth_domain'],
                        'admin': admin,
                    },
                    'preferences': {},
                    'favorites': []
                }
                session.DB.ES.index(index=session.DB.dbname, doc_type='account', id = cid, body = user)
            sess = {
                'timestamp': int(time.time()),
                'cid': cid
            }
            session.DB.ES.index(index=session.DB.dbname, doc_type='uisession', id = session.cookie, body = sess)
            yield json.dumps({"okay": True, "msg": "Logged in successfully"})
        else:
            yield json.dumps({"okay": False, "msg": "Could not log in via OAuth: Backend did not return proper credentials."})
    
    else:
        yield json.dumps({"okay": False, "msg": "Unrecognized OAuth parameters!"})
    
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
This is the user account handler for Kibble.
adds, removes and edits accounts.
"""

import json
import re
import time
import bcrypt

def run(API, environ, indata, session):
    
    method = environ['REQUEST_METHOD']
    
    # Add a new account??
    if method == "PUT":
        u = indata['email']
        p = indata['password']
        d = indata['displayname']
        
        # Are new accounts allowed? (admin can always make accounts, of course)
        if not session.config['accounts'].get('allowSignup', False):
            if not (session.user and session.user['level'] == 'admin'):
                raise API.exception(403, "New account requests have been administratively disabled.")
        
        # Check if we already have that username in use
        if session.DB.ES.exists(index=session.DB.dbname, doc_type='useraccount', id = u):
            raise API.exception(403, "Username already in use")
        
        # We require a username, displayName password of at least 3 chars each
        if len(p) < 3 or len(u) < 3 or len(d) < 3:
            raise API.exception(400, "Username, display-name and password must each be at elast 3 characters long.")
        
        # We loosely check that the email is an email
        if not re.match(r"^\S+@\S+\.\S+$", u):
            raise API.exception(400, "Invalid email address presented.")
        
        # Okay, let's make an account...I guess
        salt = bcrypt.gensalt()
        pwd = bcrypt.hashpw(p.encode('utf-8'), salt).decode('ascii')
        
        doc = {
            'email': u,                         # Username (email)
            'password': pwd,                    # Hashed password
            'displayName': d,                   # Display Name
            'organisations': [],                # Orgs user belongs to (default is none)
            'ownerships': [],                   # Orgs user owns (default is none)
            'defaultOrganisation': None,        # Default org for user
            'verified': False,                  # Account verified via email?
            'userlevel': "user"                 # User level (user/admin)
        }
        
        # If we have auto-invite on, check if there are orgs to invite to
        if 'autoInvite' in session.config['accounts']:
            dom = u.split('@')[-1].lower()
            for ai in session.config['accounts']['autoInvite']:
                if ai['domain'] == dom:
                    doc['organisations'].append(ai['organisation'])
                
        session.DB.ES.index(index=session.DB.dbname, doc_type='useraccount', id = u, body = doc)
        yield json.dumps({"message": "Account created!"})
        return
    
    # We need to be logged in for the rest of this!
    if not session.user:
        raise API.exception(403, "You must be logged in to use this API endpoint! %s")
    

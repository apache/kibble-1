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
# OPENAPI-URI: /api/verify/{email}/{vcode}
########################################################################
# get:
#      summary: Verify an account
#      parameters:
#        - name: email
#          in: path
#          description: Email address of account
#          required: true
#          schema:
#            type: string
#        - name: vcode
#          in: path
#          description: Verification code
#          required: true
#          schema:
#            type: string
#      responses:
#        '200':
#          description: 200 Response
#          content:
#            application/json:
#              schema:
#                $ref: '#/components/schemas/ActionCompleted'
#        default:
#          description: unexpected error
#          content:
#            application/json:
#              schema:
#                $ref: '#/components/schemas/Error'
# 
########################################################################





"""
This is the user account verifier for Kibble.
"""


def run(API, environ, indata, session):
    
    # Get vocde, make sure it's 40 chars
    vcode = indata.get('vcode')
    if len(vcode) != 40:
        raise API.exception(400, "Invalid verification code!")
    
    # Find the account with this vcode
    email = indata.get('email')
    if len(email) < 7:
        raise API.exception(400, "Invalid email address presented.")
    
    if session.DB.ES.exists(index=session.DB.dbname, doc_type='useraccount', id = email):
        doc = session.DB.ES.get(index=session.DB.dbname, doc_type='useraccount', id = email)
        # Do the codes match??
        if doc['_source']['vcode'] == vcode:
            doc['_source']['verified'] = True
            # Save account as verified
            session.DB.ES.index(index=session.DB.dbname, doc_type='useraccount', id = email, body = doc['_source'])
            yield("Your account has been verified, you can now log in!")
        else:
            raise API.exception(404, "Invalid verification code presented!")
    else:
        raise API.exception(404, "Invalid verification code presented!") # Don't give away if such a user exists, pssst
    
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
# OPENAPI-URI: /api/org/members
########################################################################
# get:
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/OrgMembers'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Lists the members of an organisation
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
#               $ref: '#/components/schemas/OrgMembers'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Lists the members of an organisation
# put:
#   requestBody:
#     content:
#       application/json:
#         schema:
#           $ref: '#/components/schemas/UserAccountEdit'
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
#   summary: Invite a person to an organisation
# delete:
#   requestBody:
#     content:
#       application/json:
#         schema:
#           $ref: '#/components/schemas/UserAccountEdit'
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
#   summary: Remove a person from an organisation
# 
########################################################################





"""
This is the Org list renderer for Kibble
"""

import json
import time
import hashlib

def canInvite(session):
    """ Determine if the user can edit sources in this org """
    if session.user['userlevel'] == 'admin':
        return True
    
    dOrg = session.user['defaultOrganisation'] or "apache"
    if session.DB.ES.exists(index=session.DB.dbname, doc_type="organisation", id= dOrg):
        xorg = session.DB.ES.get(index=session.DB.dbname, doc_type="organisation", id= dOrg)['_source']
        if session.user['email'] in xorg['admins']:
            return True


def run(API, environ, indata, session):
    now = time.time()
    # We need to be logged in for this!
    if not session.user:
        raise API.exception(403, "You must be logged in to use this API endpoint!")
    
    method = environ['REQUEST_METHOD']
    
    #################################################
    # Inviting a new member?                        #
    #################################################
    if method == "PUT":
        if canInvite(session):
            newmember = indata.get('email')
            isadmin = indata.get('admin', False)
            orgid = session.user['defaultOrganisation'] or "apache"
            # Make sure the org exists
            if not session.DB.ES.exists(index=session.DB.dbname, doc_type='organisation', id = orgid):
                raise API.exception(403, "No such organisation!")
            
            # make sure the user account exists
            if not session.DB.ES.exists(index=session.DB.dbname, doc_type='useraccount', id = newmember):
                raise API.exception(403, "No such user!")
            
            # Modify user account
            doc = session.DB.ES.get(index=session.DB.dbname, doc_type='useraccount', id = newmember)
            if orgid not in doc['_source']['organisations']: # No duplicates, please
                doc['_source']['organisations'].append(orgid)
                session.DB.ES.index(index=session.DB.dbname, doc_type='useraccount', id = newmember, body = doc['_source'])
            
            
            # Get org doc from ES
            doc = session.DB.ES.get(index=session.DB.dbname, doc_type='organisation', id = orgid)
            if isadmin:
                if newmember not in doc['_source']['admins']:
                    doc['_source']['admins'].append(newmember)
                    # Override old doc
                    session.DB.ES.index(index=session.DB.dbname, doc_type='organisation', id = orgid, body = doc['_source'])
                    time.sleep(1) # Bleh!!
            
            # If an admin, and not us, and reinvited, we purge the admin bit
            elif newmember in doc['_source']['admins']:
                if newmember == session.user['email']:
                    raise API.exception(403, "You can't remove yourself from an organisation.")
                doc['_source']['admins'].remove(newmember)
                # Override old doc
                session.DB.ES.index(index=session.DB.dbname, doc_type='organisation', id = orgid, body = doc['_source'])
                time.sleep(1) # Bleh!!
            yield json.dumps({"okay": True, "message": "Member invited!!"})
            
            return
        else:
            raise API.exception(403, "Only administrators or organisation owners can invite new members.")
        
    #################################################
    # DELETE: Remove a member                       #
    #################################################
    if method == "DELETE":
        if canInvite(session):
            memberid = indata.get('email')
            isadmin = indata.get('admin', False)
            orgid = session.user['defaultOrganisation'] or "apache"
            
            # We can't remove ourselves!
            if memberid == session.user['email']:
                raise API.exception(403, "You can't remove yourself from an organisation.")
            
            # Make sure the org exists
            if not session.DB.ES.exists(index=session.DB.dbname, doc_type='organisation', id = orgid):
                raise API.exception(403, "No such organisation!")
            
            # make sure the user account exists
            if not session.DB.ES.exists(index=session.DB.dbname, doc_type='useraccount', id = memberid):
                raise API.exception(403, "No such user!")
            
            # Modify user account
            doc = session.DB.ES.get(index=session.DB.dbname, doc_type='useraccount', id = memberid)
            if orgid in doc['_source']['organisations']: # No duplicates, please
                doc['_source']['organisations'].remove(orgid)
                session.DB.ES.index(index=session.DB.dbname, doc_type='useraccount', id = memberid, body = doc['_source'])
            
            # Check is user is admin and remove if so
            # Get org doc from ES
            doc = session.DB.ES.get(index=session.DB.dbname, doc_type='organisation', id = orgid)
            if memberid in doc['_source']['admins']:
                doc['_source']['admins'].remove(memberid)
                # Override old doc
                session.DB.ES.index(index=session.DB.dbname, doc_type='organisation', id = orgid, body = doc['_source'])
                time.sleep(1) # Bleh!!
                
            yield json.dumps({"okay": True, "message": "Member removed!"})
            return
        else:
            raise API.exception(403, "Only administrators or organisation owners can invite new members.")
    

    #################################################
    # GET/POST: Display members                     #
    #################################################
    if method in ["GET", "POST"]:
        orgid = session.user['defaultOrganisation'] or "apache"
        if not session.DB.ES.exists(index=session.DB.dbname, doc_type='organisation', id = orgid):
            raise API.exception(403, "No such organisation!")
        
        # Only admins should be able to view this!
        if not canInvite(session):
            raise API.exception(403, "Only organisation owners can view this list.")
        
        # Find everyone affiliated with this org
        query = {
                    'query': {
                        'bool': {
                            'must': [
                                {
                                    'term': {
                                        'organisations': orgid
                                    }
                                }
                            ]
                        }
                    }
                }
        res = session.DB.ES.search(
                index=session.DB.dbname,
                doc_type="useraccount",
                size = 5000, # TO-DO: make this a scroll??
                body = query
            )
        members = []
        for doc in res['hits']['hits']:
            members.append(doc['_id'])
        
        # Get org doc from ES
        doc = session.DB.ES.get(index=session.DB.dbname, doc_type='organisation', id = orgid)
        JSON_OUT = {
            'members': members,
            'admins': doc['_source']['admins'],
            'okay': True,
            'responseTime': time.time() - now
        }
        yield json.dumps(JSON_OUT)

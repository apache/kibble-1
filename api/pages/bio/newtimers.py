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
# OPENAPI-URI: /api/bio/newtimers
########################################################################
# get:
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Biography'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Shows some facts about a contributor
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
#             $ref: '#/components/schemas/Biography'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Shows some facts about a contributor
# 
########################################################################





"""
This is the newtimers list renderer for Kibble
"""

import json
import time
import hashlib

def find_earlier(session, query, when, who, which, where, doctype, dOrg):
    """Find earlier document pertaining to this user. return True if found"""
    if 'aggs' in query:
        del query['aggs']
        
    rangeQuery = {'range':
                    {
                        which: {
                            'from': 0,
                            'to': time.time()
                        }
                    }
                }
    
    query['query']['bool']['must'] = [
        rangeQuery,
        {
            'term': {
                'organisation': dOrg
            }
        },
        {
            'term': {
                where: who
            }
            
        }
        ]
    query['size'] = 1
    query['sort'] = [{ which: 'asc' }]
    
    res = session.DB.ES.search(
        index=session.DB.dbname,
        doc_type=doctype,
        body = query
    )
    if res['hits']['hits']:
        doc = res['hits']['hits'][0]['_source']
        if doc[which] >= when:
            return [doc[which], doc]
        else:
            return [-1, None]
    else:
        return [-1, None]
    

def run(API, environ, indata, session):
    
    # We need to be logged in for this!
    if not session.user:
        raise API.exception(403, "You must be logged in to use this API endpoint! %s")
    
    now = time.time()
    
    # First, fetch the view if we have such a thing enabled
    viewList = []
    if indata.get('view'):
        viewList = session.getView(indata.get('view'))
    if indata.get('subfilter'):
        viewList = session.subFilter(indata.get('subfilter'), view = viewList) 
    
    
    dOrg = session.user['defaultOrganisation'] or "apache"
    
    
    # Keep track of all contributors, and newcomers
    contributors = []
    newcomers = {}
    
    ####################################################################
    # Start by grabbing all contributors this period via terms agg     #
    ####################################################################
    dateTo = indata.get('to', int(time.time()))
    dateFrom = indata.get('from', dateTo - (86400*30*6)) # Default to a 6 month span
    
    
    
    
    ############################
    # CODE NEWTIMERS           #
    ############################
    rangeKey = 'ts'
    rangeQuery = {'range':
                    {
                        rangeKey: {
                            'from': dateFrom,
                            'to': dateTo
                        }
                    }
                }
    
    query = {
                'query': {
                    'bool': {
                        'must': [
                            rangeQuery,
                            {
                                'term': {
                                    'organisation': dOrg
                                }
                            }
                        ]
                    }
                }
            }
    
    query['aggs'] = {
        'by_committer': {
            'terms': {
                'field': 'committer_email',
                'size': 500
            }                
        },
        'by_author': {
            'terms': {
                'field': 'author_email',
                'size': 500
            }                
        }
    }
    
    # Source-specific or view-specific??
    if indata.get('source'):
        query['query']['bool']['must'].append({'term': {'sourceID': indata.get('source')}})
    elif viewList:
        query['query']['bool']['must'].append({'terms': {'sourceID': viewList}})
    
    
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="code_commit",
            body = query
        )
    
    code_contributors = []
    for bucket in res['aggregations']['by_committer']['buckets']:
        email = bucket['key']
        if email not in code_contributors:
            code_contributors.append(email)
    
    for bucket in res['aggregations']['by_author']['buckets']:
        email = bucket['key']
        if email not in code_contributors:
            code_contributors.append(email)
    
    # Now, for each contributor, find if they have done anything before
    for email in code_contributors:
        ea = find_earlier(session, query, dateFrom, email, 'ts', 'author_email', 'code_commit', dOrg)
        ec = find_earlier(session, query, dateFrom, email, 'ts', 'committer_email', 'code_commit', dOrg)
        if ea[0] != -1 and ec[0] != -1:
            earliest = ea
            if earliest[0] == -1 or (earliest[0] > ec[0] and ec[0] != -1):
                earliest = ec
            newcomers[email] = {
                'code': earliest
            }
    
    
    
    ############################
    # ISSUE NEWTIMERS          #
    ############################
    rangeKey = 'created'
    rangeQuery = {'range':
                    {
                        rangeKey: {
                            'from': dateFrom,
                            'to': dateTo
                        }
                    }
                }
    
    query = {
                'query': {
                    'bool': {
                        'must': [
                            rangeQuery,
                            {
                                'term': {
                                    'organisation': dOrg
                                }
                            }
                        ]
                    }
                }
            }
    
    query['aggs'] = {
        'by_creator': {
            'terms': {
                'field': 'issueCreator',
                'size': 500
            }                
        },
        'by_closer': {
            'terms': {
                'field': 'issueCloser',
                'size': 500
            }                
        }
    }
    
    # Source-specific or view-specific??
    if indata.get('source'):
        query['query']['bool']['must'].append({'term': {'sourceID': indata.get('source')}})
    elif viewList:
        query['query']['bool']['must'].append({'terms': {'sourceID': viewList}})
    
    
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="issue",
            body = query
        )
    
    issue_contributors = []
    for bucket in res['aggregations']['by_creator']['buckets']:
        email = bucket['key']
        if email not in issue_contributors:
            issue_contributors.append(email)
    
    for bucket in res['aggregations']['by_closer']['buckets']:
        email = bucket['key']
        if email not in issue_contributors:
            issue_contributors.append(email)
    
    # Now, for each contributor, find if they have done anything before
    for email in issue_contributors:
        ecr = find_earlier(session, query, dateFrom, email, 'created', 'issueCreator', 'issue', dOrg)
        ecl = find_earlier(session, query, dateFrom, email, 'closed', 'issueCloser', 'issue', dOrg)
        if ecr[0] != -1 and ecl[0] != -1:
            earliest = ecr
            if earliest[0] == -1 or (earliest[0] > ecl[0] and ecl[0] != -1):
                earliest = ecl
            newcomers[email] = newcomers.get(email, {})
            newcomers[email]['issue'] = earliest
    
    email_contributors = []
    
    ################################
    # For each newtimer, get a bio #
    ################################
    
    for email in newcomers:
        pid = hashlib.sha1( ("%s%s" % (dOrg, email)).encode('ascii', errors='replace')).hexdigest()
        person = {}
        if session.DB.ES.exists(index=session.DB.dbname, doc_type="person", id = pid):
            person = session.DB.ES.get(index=session.DB.dbname, doc_type="person", id = pid)['_source']
        person['md5'] = hashlib.md5(person['email'].encode('utf-8')).hexdigest() # gravatar needed for UI!
        newcomers[email]['bio'] = person
    
    newcomers_code = []
    newcomers_issues = []
    newcomers_email = []
    
    # Count newcomers in each category (TODO: put this elsewhere earlier)
    for email, entry in newcomers.items():
        if 'code' in entry:
            newcomers_code.append(email)
        if 'issue' in entry:
            newcomers_issues.append(email)
        if 'email' in entry:
            newcomers_email.append(email)
    
    JSON_OUT = {
        'okay': True,
        'stats': {
            'code': {
                'newcomers': newcomers_code,
                'seen': len(code_contributors),
            },
            'issues': {
                'newcomers': newcomers_issues,
                'seen': len(issue_contributors),
            },
            'email': {
                'newcomers': newcomers_email,
                'seen': len(email_contributors),
            }
        },
        'bios': newcomers,
        'responseTime': time.time() - now
    }
    yield json.dumps(JSON_OUT, indent = 2)

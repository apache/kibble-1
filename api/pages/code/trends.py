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
# OPENAPI-URI: /api/code/trends
########################################################################
# get:
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Trend'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Shows trend data for a set of repos over a given period of time
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
#             $ref: '#/components/schemas/Trend'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Shows trend data for a set of repos over a given period of time
# 
########################################################################





"""
This is the SLoC renderer for Kibble
"""

import json
import time

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
    
    
    dateTo = indata.get('to', int(time.time()))
    dateFrom = indata.get('from', dateTo - (86400*30*6)) # Default to a 6 month span
    if dateFrom < 0:
        dateFrom = 0
    dateYonder = dateFrom - (dateTo - dateFrom)
    
    
    
    ####################################################################
    # We start by doing all the queries for THIS period.               #
    # Then we reset the query, and change date to yonder-->from        #
    # and rerun the same queries.                                      #
    ####################################################################
    dOrg = session.user['defaultOrganisation'] or "apache"
    query = {
                'query': {
                    'bool': {
                        'must': [
                            {'range':
                                {
                                    'tsday': {
                                        'from': dateFrom,
                                        'to': dateTo
                                    }
                                }
                            },
                            {
                                'term': {
                                    'organisation': dOrg
                                }
                            }
                        ]
                    }
                }
            }
    # Source-specific or view-specific??
    if indata.get('source'):
        query['query']['bool']['must'].append({'term': {'sourceID': indata.get('source')}})
    elif viewList:
        query['query']['bool']['must'].append({'terms': {'sourceID': viewList}})
    if indata.get('email'):
        query['query']['bool']['should'] = [{'term': {'committer_email': indata.get('email')}}, {'term': {'author_email': indata.get('email')}}]
        query['query']['bool']['minimum_should_match'] = 1
        
    # Path filter?
    if indata.get('pathfilter'):
        pf = indata.get('pathfilter')
        if '!' in pf:
            pf = pf.replace('!', '')
            query['query']['bool']['must_not'] = query['query']['bool'].get('must_not', [])
            query['query']['bool']['must_not'].append({'regexp': {'files_changed': pf}})
        else:
            query['query']['bool']['must'].append({'regexp': {'files_changed': pf}})
    
    # Get number of commits, this period
    res = session.DB.ES.count(
            index=session.DB.dbname,
            doc_type="code_commit",
            body = query
        )
    no_commits = res['count']
    
    
    # Get number of committers, this period
    query['aggs'] = {
            'commits': {
                'cardinality': {
                    'field': 'committer_email'
                }
            },
            'authors': {
                'cardinality': {
                    'field': 'author_email'
                }
            }
            
        }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="code_commit",
            size = 0,
            body = query
        )
    no_committers = res['aggregations']['commits']['value']
    no_authors = res['aggregations']['authors']['value']
    
    
    # Get number of insertions, this period
    query['aggs'] = {
            'changes': {
                'sum': {
                    'field': 'insertions'
                }
            }
        }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="code_commit",
            size = 0,
            body = query
        )
    insertions = res['aggregations']['changes']['value']
    
    # Get number of deletions, this period
    query['aggs'] = {
            'changes': {
                'sum': {
                    'field': 'deletions'
                }
            }
        }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="code_commit",
            size = 0,
            body = query
        )
    deletions = res['aggregations']['changes']['value']
    
    
    ####################################################################
    # Change to PRIOR SPAN                                             #
    ####################################################################
    dOrg = session.user['defaultOrganisation'] or "apache"
    query = {
                'query': {
                    'bool': {
                        'must': [
                            {'range':
                                {
                                    'tsday': {
                                        'from': dateYonder,
                                        'to': dateFrom-1
                                    }
                                }
                            },
                            {
                                'term': {
                                    'organisation': dOrg
                                }
                            }
                        ]
                    }
                }
            }
    # Source-specific or view-specific??
    if indata.get('source'):
        query['query']['bool']['must'].append({'term': {'sourceID': indata.get('source')}})
    elif viewList:
        query['query']['bool']['must'].append({'terms': {'sourceID': viewList}})
        
    # Path filter?
    if indata.get('pathfilter'):
        pf = indata.get('pathfilter')
        if '!' in pf:
            pf = pf.replace('!', '')
            query['query']['bool']['must_not'] = query['query']['bool'].get('must_not', [])
            query['query']['bool']['must_not'].append({'regexp': {'files_changed': pf}})
        else:
            query['query']['bool']['must'].append({'regexp': {'files_changed': pf}})
    
    
    # Get number of commits, this period
    res = session.DB.ES.count(
            index=session.DB.dbname,
            doc_type="code_commit",
            body = query
        )
    no_commits_before = res['count']
    
    # Get number of committers, this period
    query['aggs'] = {
            'commits': {
                'cardinality': {
                    'field': 'committer_email'
                }
            },
            'authors': {
                'cardinality': {
                    'field': 'author_email'
                }
            }
        }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="code_commit",
            size = 0,
            body = query
        )
    no_committers_before = res['aggregations']['commits']['value']
    no_authors_before = res['aggregations']['authors']['value']
    
    # Get number of insertions, this period
    query['aggs'] = {
            'changes': {
                'sum': {
                    'field': 'insertions'
                }
            }
        }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="code_commit",
            size = 0,
            body = query
        )
    insertions_before = res['aggregations']['changes']['value']
    
     # Get number of deletions, this period
    query['aggs'] = {
            'changes': {
                'sum': {
                    'field': 'deletions'
                }
            }
        }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="code_commit",
            size = 0,
            body = query
        )
    deletions_before = res['aggregations']['changes']['value']
    
    
    
    trends = {
        "committers": {
            'before': no_committers_before,
            'after': no_committers,
            'title': "Committers this period"
        },
        "authors": {
            'before': no_authors_before,
            'after': no_authors,
            'title': "Authors this period"
        },
        'commits': {
            'before': no_commits_before,
            'after': no_commits,
            'title': "Commits this period"
        },
        'changes': {
            'before': insertions_before + deletions_before,
            'after': insertions + deletions,
            'title': "Lines changed this period"
        }
    }
    
    JSON_OUT = {
        'trends': trends,
        'okay': True,
        'responseTime': time.time() - now
    }
    yield json.dumps(JSON_OUT)

"""
commits = {
                before = pcommits,
                after = commits,
                title = "Commits"
            },
            [role.."s"] = {
                before = pcommitters,
                after = committers,
                title = role:gsub("^(%S)", string.upper).."s",
            },
            lines = {
                before = pdeletions + pinsertions,
                after = deletions + insertions,
                title = "Lines changed"
            }
            """
            
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
This is the TopN committers list renderer for Kibble
"""

import json
import time
import hashlib

def run(API, environ, indata, session):
    
    # We need to be logged in for this!
    if not session.user:
        raise API.exception(403, "You must be logged in to use this API endpoint! %s")
    
    now = time.time()
    
    # First, fetch the view if we have such a thing enabled
    viewList = []
    if indata.get('view'):
        if session.DB.ES.exists(index=session.DB.dbname, doc_type="view", id = indata['view']):
            view = session.DB.ES.get(index=session.DB.dbname, doc_type="view", id = indata['view'])
            viewList = view['_source']['sourceList']
    
    dateTo = indata.get('to', int(time.time()))
    dateFrom = indata.get('from', dateTo - (86400*30*6)) # Default to a 6 month span
    
    which = 'committer_email'
    role = 'committer'
    if indata.get('author', False):
        which = 'author_email'
        role = 'author'
    
    interval = indata.get('interval', 'month')
    
    
    ####################################################################
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
    
    
    # Get top 25 committers this period
    query['aggs'] = {
            'committers': {
                'terms': {
                    'field': which,
                    'size': 25
                },
                'aggs': {
                'byinsertions': {
                    'terms': {
                        'field': which
                    },
                    'aggs': {
                        'stats': {
                            'sum': {
                                'field': "insertions"
                            }
                        }
                    }
                },
                'bydeletions': {
                    'terms': {
                        'field': which
                    },
                    'aggs': {
                        'stats': {
                            'sum': {
                                'field': "deletions"
                            }
                        }
                    }
                },
            }
            },
            
        }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="code_commit",
            size = 0,
            body = query
        )

    people = {}
    for bucket in res['aggregations']['committers']['buckets']:
        email = bucket['key']
        count = bucket['doc_count']
        sha = hashlib.sha1( ("%s%s" % (dOrg, email)).encode('utf-8') ).hexdigest()
        if session.DB.ES.exists(index=session.DB.dbname,doc_type="person",id = sha):
            pres = session.DB.ES.get(
                index=session.DB.dbname,
                doc_type="person",
                id = sha
                )
            person = pres['_source']
            person['name'] = person.get('name', 'unknown')
            people[email] = person
            people[email]['md5'] = hashlib.md5(person.get('email', 'unknown').encode('utf-8')).hexdigest()
            people[email]['changes'] = {
                'commits': count,
                'insertions': int(bucket['byinsertions']['buckets'][0]['stats']['value']),
                'deletions': int(bucket['bydeletions']['buckets'][0]['stats']['value'])
            }
        
        
    # Get timeseries for this period
    query['aggs'] = {
            'per_interval': {
                'date_histogram': {
                    'field': 'date',
                    'interval': interval
                },
                'aggs': {
                    'by_committer': {
                        'cardinality': {
                            'field': 'committer_email'
                        }
                    },
                    'by_author': {
                        'cardinality': {
                            'field': 'author_email'
                        }
                    }
                }
            }
        }
    
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="code_commit",
            size = 0,
            body = query
        )

    timeseries = []
    for bucket in res['aggregations']['per_interval']['buckets']:
        ts = int(bucket['key'] / 1000)
        ccount = bucket['by_committer']['value']
        acount = bucket['by_author']['value']
        timeseries.append({
            'date': ts,
            'committers': ccount,
            'authors': acount
        })
    
    JSON_OUT = {
        'people': people,
        'timeseries': timeseries,
        'sorted': people,
        'okay': True,
        'responseTime': time.time() - now,
        'widgetType': {
            'chartType': 'bar'
        }
    }
    yield json.dumps(JSON_OUT)

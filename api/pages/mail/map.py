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
# OPENAPI-URI: /api/mail/map
########################################################################
# get:
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Sloc'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Shows a breakdown of email author reply mappings
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
#             $ref: '#/components/schemas/Sloc'
#       description: 200 Response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Shows a breakdown of email author reply mappings
#
########################################################################





"""
This is the committer relationship list renderer for Kibble
"""

import json
import time
import hashlib
import copy
import re
import math

badBots = r"(JIRA|Hudson|jira|jenkins|GitHub|git@|dev@|bugzilla|gerrit)"

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
    span = dateTo - dateFrom

    ####################################################################
    ####################################################################
    dOrg = session.user['defaultOrganisation'] or "apache"
    query = {
                'query': {
                    'bool': {
                        'must': [
                            {'range':
                                {
                                    'ts': {
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
    if indata.get('search'):
        query['query']['bool']['must'].append({'regexp': {'subject': indata.get('search')}})

    if indata.get('email'):
        query['query']['bool']['minimum_should_match'] = 1
        query['query']['bool']['should'] = [
            {'term': {'replyto.keyword': indata.get('email')}},
            {'term': {'sender': indata.get('email')}},
            ]

    # Get number of commits, this period, per repo
    query['aggs'] = {
            'per_ml': {
                'terms': {
                    'field': 'replyto.keyword' if not indata.get('author') else 'sender',
                    'size': 150
                }
            }
        }
    res = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="email",
            size = 0,
            body = query
        )

    repos = {}
    repo_commits = {}
    authorlinks = {}
    max_emails = 0
    max_links = 0
    max_shared = 0
    max_authors = 0
    minLinks = indata.get('links', 1)

    if indata.get('email'):
            del query['query']['bool']['should']
            del query['query']['bool']['minimum_should_match']

    # For each repo, count commits and gather data on authors
    for doc in res['aggregations']['per_ml']['buckets']:
        sourceID = doc['key']
        emails = doc['doc_count']
        if re.search(badBots, sourceID): # No bots
            continue
        if emails > (span/86400)*4: # More than 4/day and we consider you a bot!
            continue


        # Gather the unique authors/committers
        query['aggs'] = {
            'per_ml': {
                'terms': {
                    'field': 'sender' if not indata.get('author') else 'replyto.keyword',
                    'size': 5000
                }
            }
        }
        xquery = copy.deepcopy(query)

        xquery['query']['bool']['must'].append({'term': {'replyto.keyword' if not indata.get('author') else 'sender': sourceID}})
        xres = session.DB.ES.search(
            index=session.DB.dbname,
            doc_type="email",
            size = 0,
            body = xquery
        )
        authors = []
        for person in xres['aggregations']['per_ml']['buckets']:
            pk = person['key']
            authors.append(pk)
        if emails > max_emails:
            max_emails = emails
        repos[sourceID] = authors
        repo_commits[sourceID] = emails

    # Now, figure out which repos share the same contributors
    repo_links = {}
    repo_notoriety = {}
    repodatas = {}
    repo_authors = {}

    # Grab data of all sources
    for ID, repo in repos.items():
        mylinks = {}
        hID = hashlib.sha1( ("%s%s" % (dOrg, ID)).encode('ascii', errors='replace')).hexdigest()
        if not session.DB.ES.exists(index=session.DB.dbname, doc_type="person", id = hID):
            continue
        repodatas[ID] = session.DB.ES.get(index=session.DB.dbname, doc_type="person", id = hID)

    for ID, repo in repos.items():
        mylinks = {}
        if not ID in repodatas:
            continue
        repodata = repodatas[ID]
        oID = ID
        if indata.get('collapse'):
            m = re.search(indata.get('collapse'), repodata['_source']['email'])
            if m:
                ID = m.group(1)
        xlinks = []
        for xID, xrepo in repos.items():
            if xID in repodatas:
                xrepodata = repodatas[xID]
                if indata.get('collapse'):
                    m = re.search(indata.get('collapse'), xrepodata['_source']['email'])
                    if m:
                        xID = m.group(1)
                if xID != ID:

                    if ID in xrepo:
                        xlinks.append(xID)
                        lname = "%s||%s" % (ID, xID) # Link name
                        rname = "%s||%s" % (xID, ID) # Reverse link name
                        if len(xlinks) > 0 and rname not in repo_links and len(xlinks) >= minLinks:
                            mylinks[ID] = mylinks.get(ID, 0) + 1
                            repo_links[lname] = repo_links.get(lname, 0) + len(xlinks) # How many contributors in common between project A and B?
                            if repo_links[lname] > max_shared:
                                max_shared = repo_links[lname]
                        elif rname in repo_links:
                            repo_links[rname] = repo_links.get(rname, 0) + len(xlinks)
        if ID not in repo_notoriety:
            repo_notoriety[ID] = set()
        repo_notoriety[ID].update(mylinks.keys()) # How many projects is this repo connected to?

        if ID not in repo_authors:
            repo_authors[ID] = set()
        repo_authors[ID].update(repo) # How many projects is this repo connected to?

        if ID != oID:
            repo_commits[ID] = repo_commits.get(ID, 0) + repo_commits[oID]
            if repo_commits[ID] > max_emails:
                max_emails = repo_commits[ID] # Used for calculating max link thickness
        if len(repo_notoriety[ID]) > max_links:
            max_links = len(repo_notoriety[ID])
        if len(repo_authors[ID]) > max_authors:
            max_authors = len(repo_authors[ID]) # Used for calculating max sphere size in charts

    # Now, pull it all together!
    nodes = []
    links = []
    existing_repos = []
    for sourceID, ns in repo_notoriety.items():
        lsize = 0
        for k in repo_links.keys():
            fr, to = k.split('||')
            if fr == sourceID or to == sourceID:
                lsize += 1
        asize = len(repo_authors[sourceID])
        doc = {
            'id': sourceID,
            'gravatar': hashlib.md5(sourceID.lower().encode('utf-8')).hexdigest(),
            'name': repodatas[sourceID]['_source'].get('name', sourceID),
            'replies': repo_commits[sourceID],
            'authors': asize,
            'links': lsize,
            'size': max(5, (1 - abs(math.log10(repo_commits[sourceID] / max_emails))) * 45),
            'tooltip': "%u connections, %u fellows, %u replies to" % (lsize, asize, repo_commits[sourceID])
        }
        nodes.append(doc)
        existing_repos.append(sourceID)

    for k, s in repo_links.items():
        size = s
        fr, to = k.split('||')
        if fr in existing_repos and to in existing_repos:
            doc = {
                'source': fr,
                'target': to,
                'value': max(1, (size/max_shared) * 5),
                'name': "%s &#8596; %s" % (fr, to),
                'tooltip': "%u topics exchanged" % size
            }
            links.append(doc)

    JSON_OUT = {
        'maxLinks': max_links,
        'maxShared': max_shared,
        'widgetType': {
            'chartType': 'link'  # Recommendation for the UI
        },
        'links': links,
        'nodes': nodes,
        'okay': True,
        'responseTime': time.time() - now
    }
    yield json.dumps(JSON_OUT)

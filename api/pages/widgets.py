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
# OPENAPI-URI: /api/widgets/{pageid}
########################################################################
#    get:
#      summary: Shows the widget layout for a specific page
#      security:
#        - cookieAuth: []
#      parameters:
#        - name: pageid
#          in: path
#          description: Page ID to fetch design for
#          required: true
#          schema:
#            type: string
#      responses:
#        '200':
#          description: 200 Response
#          content:
#            application/json:
#              schema:
#                $ref: '#/components/schemas/WidgetDesign'
#        default:
#          description: unexpected error
#          content:
#            application/json:
#              schema:
#                $ref: '#/components/schemas/Error'
########################################################################
"""
This is the widget design handler for Kibble
"""

import yaml
import json

def run(API, environ, indata, session):
    
    if not session.user:
        raise API.exception(403, "You must be logged in to use this API endpoint! %s")
    
    widgets = yaml.load(open("yaml/widgets.yaml"))
    
    page = indata['pageid']
    if not page or page == '0':
        page = widgets.get('defaultWidget', 'repos')
    if page in widgets['widgets']:
        yield json.dumps(widgets['widgets'][page])
    else:
        raise API.exception(404, "Widget design not found!")
    
    
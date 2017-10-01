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

kibbleLoginCallback = (json, state) ->
    userAccount = json
    # Everything okay, redirect to dashboard :)
    m = location.href.match(/\?redirect=(.+)$/)
    if m and not m[1].match(/:/)
        location.href = m[1]
    else
        location.href = "organisations.html?page=org"

kibbleLogin = (email, password) ->
    put("session", {email: email, password: password}, null, kibbleLoginCallback)
    return false

signout = () ->
    xdelete('session', {}, {}, () -> location.href = 'login.html')
    
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
        location.href = "/organisations.html?page=org"

kibbleLogin = (email, password) ->
    put("session", {email: email, password: password}, null, kibbleLoginCallback)
    return false

signout = () ->
    xdelete('session', {}, {}, () -> location.href = 'login.html')

accountCallback = (json, state) ->
    obj = get('signup')
    obj.innerHTML = ""
    h = new HTML('h3', {}, "Account created!")
    obj.appendChild(h)
    if json.verified
        t = new HTML('p', {}, "You can now log in and use your account")
    else
        t = new HTML('p', {}, "Please check your email account for a verification email.")
    obj.appendChild(t)
    
kibbleSignup = (form) ->
    email = form.email.value
    displayName = form.displayname.value
    password = form.password.value
    password2 = form.password2.value
    
    # Passwords must match
    if password != password2
        alert("Passwords must match!")
        return false
    
    # Username must be >= 2 chars
    if displayName.length < 2
        alert("Please enter a proper display name!")
        return false
    
    # Email must be valid
    if not email.match(/([^@]+@[^.]+\.[^.])/)
        alert("Please enter a valid email address!")
        return false
    
    put('account', {
        email: email,
        password: password,
        displayname: displayName
    }, null, accountCallback)
    
    return false
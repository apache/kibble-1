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

userAccount = { foundation: "public" }
pageID = 0
APIVERSION = 3

setupPage = (json, state) ->
    # Get rid of placeholder
    $('#placeholder').remove()

    if json.error
        div = document.getElementById('innercontents')
        div.style.textAlign = 'center'
        div.innerHTML = "<a style='color: #D44; font-size: 100pt;'><i class='fa fa-warning'></i></a><br/><h3>An error occurred:</h3><p style='font-size: 12pt;'>" + json.error + "</p>"
        return
    
    # View active?
    if userAccount.view and userAccount.view.length > 0
        vrow = new Row()
        p = mk('p')
        p.style.background = "#EEF"
        p.style.fontSize = "11pt"
        p.style.fontStyle = 'italic'
        p.style.color = "#222"
        app(p, txt("You are currently using a view to filter out sources. "))
        a = mk('a')
        app(a, txt("Click here to deactivate it"))
        set(a, 'href', 'javascript:void(activateview(null, location.href));')
        app(p, a)
        app(p, txt(" or "))
        a = mk('a')
        app(a, txt("Click here to manage views"))
        set(a, 'href', '?page=views')
        app(p, a)
        vrow.inject(p)
    
    document.title = json.title + " - Apache Kibble"    
    # Go through each row
    
    for r in json.rows
        row = new Row()

        # Add each widget
        for child in r.children

            # Make the widget box
            widget = new Widget((child.blocks || 3), child)
            if state.gargs
                widget.args.eargs = widget.args.eargs or {}
                for k, v of state.gargs
                    widget.args.eargs[k] = v
            widget.parent = row
            row.inject(widget)
            if child.eargs
                for k, v of child.eargs
                    widget.args.eargs[k] = v
            if child.wargs
                widget.wargs = {}
                for k, v of child.wargs
                    widget.wargs[k] = v
            if child.type not in ['views', 'sourcelist']
                widget.args.eargs.quick = 'true'        
            switch child.type

                when 'datepicker' then datepicker(widget)
                when 'sourcepicker' then widget.load(sourceexplorer)
                when 'repopicker' then widget.load(explorer)
                when 'mailpicker' then widget.load(mailexplorer)
                when 'issuepicker' then widget.load(issueexplorer)
                when 'forumpicker' then widget.load(forumexplorer)
                when 'viewpicker' then widget.load(viewexplorer)
                when 'logpicker' then widget.load(logexplorer)
                when 'impicker' then widget.load(imexplorer)
                when 'logpicker' then widget.load(logexplorer)
                when 'cipicker' then widget.load(ciexplorer)
                when 'widgetpicker' then widget.load(widgetexplorer)
                when 'multiviewpicker' then widget.load(multiviewexplorer)
                when 'donut' then widget.load(donut)
                when 'gauge' then widget.load(gauge)
                when 'punchcard' then widget.load(punchcard)
                when 'widget' then widget.load(publisher)
                when 'radar' then widget.load(radar)
                when 'top5' then widget.load(top5)
                when 'factors' then widget.load(factors)
                when 'trends' then widget.load(trend)
                when 'line' then widget.load(linechart)
                when 'bio' then widget.load(bio)
                when 'messages' then widget.load(messages)
                when 'sourcelist' then widget.load(sourcelist)
                when 'sourceadd' then widget.load(sourceadd)
                when 'phonebook' then widget.load(phonebook)
                when 'preferences' then widget.load(preferences)
                when 'orgadmin' then widget.load(orgadmin)
                when 'affiliations' then widget.load(affiliation)
                when 'views' then widget.load(manageviews)
                when 'paragraph' then widget.load(paragraph)
                when 'relationship' then widget.load(relationship)
                when 'treemap' then widget.load(treemap)
                when 'report' then widget.load(report)
                when 'mvp' then widget.load(mvp)
                when 'comstat' then widget.load(comstat)
                when 'worldmap' then widget.load(worldmap)
                when 'orglist' then widget.load(orglist)
                when 'membership' then widget.load(membershipList)
                when 'jsondump' then widget.load(jsondump)




loadPageWidgets = (page, apiVersion) ->
    if not page
        page = window.location.search.substr(1)
    if apiVersion
        APIVERSION = apiVersion
    # Insert spinning cog
    ph = document.createElement('div')
    ph.setAttribute("class", "row")
    ph.setAttribute("id", "placeholder")
    col = document.createElement('div')
    col.setAttribute("class", "col-md-12")
    ph.appendChild(col)
    idiv = document.createElement('div')
    idiv.setAttribute("class", "icon")
    idiv.setAttribute("style", "text-align: center; vertical-align: middle; height: 500px;")
    i = document.createElement('i')
    i.setAttribute("class", "fa fa-spin fa-cog")
    i.setAttribute("style", "font-size: 240pt !important; color: #AAB;")
    idiv.appendChild(i)
    idiv.appendChild(document.createElement('br'))
    idiv.appendChild(document.createTextNode('Loading, hang on tight..!'))
    col.appendChild(idiv)
    ph.appendChild(col)

    document.getElementById('innercontents').innerHTML = ""
    document.getElementById('innercontents').appendChild(ph)

    while page.match(/([^=]+)=([^=&]+)&?/)
        m = page.match(/([^=]+)=([^&=]+)&?/)
        if m
            console.log(m[1] + "=" + m[2])
            globArgs[m[1]] = unescape(m[2])
            page = page.replace(m[0], '')
    if globArgs.page
        pageID = globArgs.page

    if globArgs.view
        $( "a" ).each( () ->
            url = $(this).attr('href')
            m = url.match(/^(.+\?page=[-a-z]+)(?:&view=[a-f0-9]+)?(.*)$/)
            if m
                if globArgs.view
                        $(this).attr('href', "#{m[1]}&view=#{globArgs.view}#{m[2]}")
                
        )
    # Fetch account info
    fetch('session', null, renderAccountInfo)


renderAccountInfo = (json, state) ->
    if json.error
        div = document.getElementById('innercontents')
        div.style.textAlign = 'center'
        div.innerHTML = "<a style='color: #D44; font-size: 100pt;'><i class='fa fa-warning'></i></a><br/><h3>An error occurred:</h3><p style='font-size: 12pt;'>" + json.error + "</p>"
        if json.loginRequired
            location.href = "/login.html"
    else
        userAccount = json
        img = document.getElementById('user_image')
        img.setAttribute("src", "https://secure.gravatar.com/avatar/" + json.gravatar + ".png")
    
        name = document.getElementById('user_name')
        name.innerHTML = ""
        name.appendChild(document.createTextNode(json.displayName))
    
        ulevel = get('user_level')
        ulevel.inject(if json.userlevel == 'admin' then 'Administrator' else if json.defaultOrganisation in json.ownerships then 'Organisation Owner' else 'User')
        
        nm = get('messages_number')
        nm.innerHTML = json.messages
        if json.messages > 0
            nm.setAttribute("class", "badge bg-green")
            nl = get('messages_list')
            for email in json.messages_headers
                mli = mk('li')
                ma = mk('a')
                set(ma, 'href', '?page=messages&message=' + email.id)
                msp = mk('span')
                set(msp, 'class', 'image')
                img = mk('img')
                set(img, 'src', 'https://secure.gravatar.com/avatar/' + email.gravatar + ".png?d=identicon")
                app(msp, img)
                app(ma, msp)
                msp = mk('span')
                app(msp, txt(email.senderName))
                app(ma, msp)
                
                msp = mk('span')
                set(msp, 'class', 'message')
                app(msp, txt(email.subject))
                app(ma, msp)
                app(mli, ma)
                app(nl, mli)
            
        # Fetch widget list
        fetch('widgets/' + pageID, { gargs: globArgs }, setupPage)

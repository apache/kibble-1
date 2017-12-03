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

addsources = (form) ->
    rv = get('retval')
    cog(rv)
    json = {
        action: 'add',
        sources: []
    }
    lines = form.sources.value.split(/\r?\n/g)
    creds = null
    noclone = false
    if form.noclone.checked
        noclone = true
    if form.auth.checked
        creds = {
            type: form.atype.value,
            username: form.auser.value,
            password: form.apass.value,
            cookie: form.acookie.value
        }
    for line in lines
        if line.length > 5
            json.sources.push({
                organisation: userAccount.organisation,
                sourceURL: line,
                type: form.stype.value,
                creds: creds,
                noclone: noclone
            })
    put('sources', json, null, sourceret)
    return false

redirs = () -> location.href = '?page=sources'

sourceret = (json, state) ->
    rv = get('retval')
    if json.completed
        rv.style.fontSize = "20pt"
        rv.style.color = "#383";
        json.added = json.added or 0
        rv.innerHTML = json.added + " sources added"
        if json.updated and json.updated > 0
            rv.innerHTML += ", " + json.updated + " updated."
        if json.unknowns and json.unknowns > 0
            rv.innerHTML += ", " + json.unknowns + " sources could not be added (unknown source type?)"
        window.setTimeout(redirs, 2000)
    else
        rv.style.fontSize = "20pt"
        rv.style.color = "#843";
        rv.innerHTML = "<h2>Error: </h2>" + json.error

deletesource = (hash) ->
    if window.confirm("Are you sure you wish to delete this resource?\nNOTE: Not everything about this can be deleted. Due to the nature of especially git, the unique commit stats will NOT change when you delete a git resource until you force a complete reindex of everything.")
        tr = get(hash)
        tr.parentNode.removeChild(tr)
        xdelete('sources', { id: hash }, null, null)
       
sourceTypes = {
    
}
getSourceType = (main, t) ->
    if not sourceTypes[t]
        obj = new HTML('div', { id: "source_#{t}", style: { display: "none" }})
        tbl = mk('table')
        set(tbl, 'class', 'table table-striped')
        thead = mk('thead')
        tr = mk('tr')
        for el in ['Source', 'Progress', 'Last Update',  'Status', 'Actions']
            td = mk('th')
            if el.match(/Last/)
                td.style.width = "200px"
                td.style.textAlign = 'right'
            if el.match(/Status/)
                td.style.width = "600px"
            app(td, txt(el))
            app(tr, td)
        app(thead, tr)
        app(tbl, thead)
        
        tbody = new HTML('tbody')
        app(tbl, tbody)
        obj.inject(tbl)
        main.inject(obj)
        sourceTypes[t] = {
            main: obj,
            div: tbody,
            count: 0
        }
    return sourceTypes[t]

sourcelist = (json, state) ->
    
    slist = mk('div')
    vlist = new HTML('div')
    if json.sources
        sources = json.sources
        for source in sources
            source.good = true
            source.running = false
            steps = ['sync', 'census', 'count', 'evolution']
            if source.type == 'mail'
                steps = ['mail']
            if source.type in ['jira', 'bugzilla']
                steps = ['issues']
            if source.type in ['irc']
                steps = ['census']
            if source.type == 'gerrit' or source.type == 'github'
                steps = ['issues', 'sync', 'census', 'count', 'evolution']
            for item in steps
                if source.steps
                    if source.steps[item] and source.steps[item].good == false
                        source.good = false
                    if source.steps[item] and source.steps[item].running
                        source.running = true
        sources = if sources.sort then sources else []
        sources.sort((a,b) ->        return (                if a.running == b.running then                    (if a.good == b.good then                     (if a.sourceURL > b.sourceURL then 1 else -1)                     else (if b.good == true then -1 else 1)                        )                else (if (b.running == true) then 1 else -1)                ))
        for source in sources
            st = getSourceType(vlist, source.type)
            tbody = st.div
            st.count++;
            d = mk('tr')
            set(d, 'id', source.sourceID)
            set(d, 'scope', 'row')
            
            
            t = mk('td')
            t.style.color = "#369"
            app(t, txt(source.sourceURL))
            app(d, t)
            
            # Progress
            lastUpdate = 0
            lastFailure = null
            lastException = null
            running = null
            firstRun = 0
            icons =
                sync: 'fa fa-download',
                census: 'fa fa-users',
                count: 'fa fa-sitemap',
                evolution: 'fa fa-signal'
                mail: 'fa fa-envelope'
                issues: 'fa fa-feed'
                
            t = new HTML('td', { style: { minWidth: "260px !important"}})
        
            borked = false
            steps = ['sync', 'census', 'count', 'evolution']
            if source.type in ['mail', 'ponymail', 'pipermail', 'hyperkitty']
                steps = ['mail']
            if source.type in ['jira', 'bugzilla']
                steps = ['issues']
            if source.type in ['gerrit', 'gitlab', 'github']
                steps = ['sync', 'census', 'count', 'evolution', 'issues']
            if source.type in ['irc', 'stats']
                steps = ['census']
            for item in steps
                color = "#394"
                cl = icons[item]
                if not source.steps or not source.steps[item] or borked
                    color = "#777"
                    desc = item + ": This step hasn't completed yet"
                else
                    if source.steps[item].time > lastUpdate
                        lastUpdate = source.steps[item].time
                    desc = source.steps[item].status
                    if source.steps[item].good == false
                        borked = true
                        color = "#952"
                        lastFailure = source.steps[item].status
                        lastException = source.steps[item].exception
                    if source.steps[item].running
                        cl += " fa-bubble"
                        running = source.steps[item].status
                        color = "#359"
                ic = mk('i')
                ic.style.padding = "10px"
                ic.style.fontSize = "20pt"
                set(ic, 'class', cl)
                set(ic, 'title', desc)
                ic.style.color = color
                app(t, ic)
            if borked
                set(t, 'data-steps-failure', 'true')
            else
                set(t, 'data-steps-failure', 'false')
            t.style.minWidth = "260px"
            app(d, t)
                    
            lu = "Unknown"
            if lastUpdate > 0
                lu = ""
                t = (new Date().getTime()/1000) - lastUpdate
                h = Math.floor(t / 3600)
                m = Math.floor((t % 3600)/60)
                if h > 0
                    lu = h + " hour" + (if h == 1 then '' else 's') + ", "
                lu += m + " minute" + (if m == 1 then '' else 's') + " ago."
                
            t = mk('td')
            t.style.textAlign = 'right'
            t.style.color = "#963"
            t.style.width = "200px !important"
            app(t, txt(lu))
            app(d, t)
            
            
            
            status = mk('td')
            status.style.width = "600px !important"
            if lastFailure
                status.style.color = "#843"
                app(status, txt(lastFailure))
                if lastException
                    app(status, mk('br'))
                    app(status, txt("Exception: " + lastException))
                app(d, status)
            else
                if lastUpdate == 0
                    app(status, txt("Source hasn't been processed yet..."))
                else
                    if running
                        app(status, txt(running))
                    else
                        app(status, txt("No errors detected."))
                app(d, status)
            
            act = mk('td')
            dbtn = mk('button')
            set(dbtn, 'class', 'btn btn-danger')
            set(dbtn, 'onclick', 'deletesource("' + source.sourceID + '");')
            dbtn.style.padding = "2px"
            app(dbtn, txt("Delete"))
            app(act, dbtn)
            
            app(d, act)
            tbody.inject(d)
        
        for t, el of sourceTypes
            div = new HTML('div', {class: "sourceTypeIcon", onclick: "showType('#{t}');"})
            el.btn = div
            img = new HTML('img', { src: "images/sourcetypes/#{t}.png", style: {  width: "32px", margin: "2px", cursor: "pointer"}, title: t})
            div.inject(img)
            div.inject(" #{t}: #{el.count}")
            slist.inject(div)
    #app(slist, tbl)
    state.widget.inject(slist, true)
    state.widget.inject(vlist)
    
    retval = mk('div')
    set(retval, 'id', 'retval')
    state.widget.inject(retval)
    showType(true) # Show first available type
    
showType = (t) ->
    for st, el of sourceTypes
        if st == t or t == true
            t = "blargh"
            el.btn.className = "sourceTypeIcon selected"
            el.main.style.display = "block"
        else
            el.btn.className = "sourceTypeIcon"
            el.main.style.display = "none"

addSourceType = (t) ->
    for st, el of aSourceTypes
        if st == t
            el.style.display = "block"
        else
            el.style.display = "none"

aSourceTypes = {}
st = {}
sourceadd = (json, state) ->
    div = new HTML('div', style: { position: "relative"})
    div.inject(new HTML('h3', {}, "Source type:"))
    st = json
    for type, el of json
        aSourceTypes[type] = new HTML('form', { style: { float: "left", background: "#FFE", border: "2px solid #333", margin: "20px", borderRadius: "10px", padding: "20px", display: "none"}})
        obj = aSourceTypes[type]
        obj.inject(new HTML("h4", {}, el.title+":"))
        opt = new HTML('input', { onclick: "addSourceType('#{type}');", type: "radio", id: "type_#{type}", name: "type", style: {width: "16px", height: "16px"}})
        lbl = new HTML('label', { 'for': "type_#{type}", style: {marginRight: "20px", }}, [
            new HTML('img', { src: "images/sourcetypes/#{type}.png", width: "32", height: "32"}),
            type
        ])
        div.inject(opt)
        div.inject(lbl)
        obj.inject(new HTML('p', {}, el.description or ""))
        obj.inject(keyValueForm('textarea', 'source', 'Source URL/ID:', "For example: " + el.example + ". You can add multiple sources, one per line."))
        
        if el.optauth
            obj.inject((if el.authrequired then "Required" else "Optional") + " authentication options:")
            for abit in el.optauth
                obj.inject(keyValueForm('text', "#{abit}", abit))
        btn = new HTML('input', {class: "btn btn-primary btn-block", type: "button", onclick: "addSources('#{type}', this.form);", value: "Add source(s)"})
        obj.inject(btn)
    state.widget.inject(div, true)
    for k, v of aSourceTypes
        state.widget.inject(v)
    
sourceAdded = (json, state) ->
    window.setTimeout(() ->
            location.reload()
        , 1000)
    
addSources = (type, form) ->
    jsa = []
    lineNo = 0
    re = new RegExp(st[type].regex)
    for source in form.elements.namedItem('source').value.split(/\r?\n/)
        lineNo++
        if not source.match(re)
            alert("Source on line #{lineNo} does not match the required source regex #{st[type].regex}!")
            return false
        js = {
            type: type,
            sourceURL: source
        }
        for el in form.elements
            if el.name.length > 0 and el.name != 'source'
                js[el.name] = el.value
        jsa.push(js)
    put('sources', {sources: jsa}, {}, sourceAdded)

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

# Widget Class and helper functions

widgetCache = []

findWidget = (id) ->
    for w in widgetCache
        if w.id == id
            return w
    return null


toFullscreen = (id) ->
    obj = get(id)
    FSA = get('FS_' + id)
    FSA.innerHTML = "Pop back"
    FSA.setAttribute("onclick", "toNormal('" + id + "');")
    
    CW = get('CW_' + id)
    CW.setAttribute("onclick", "toNormal('" + id + "');")
    
    w = findWidget(id)
    w.parent = obj.parentNode
    w.sibling = null
    nxt = null
    dobrk = false
    for node in w.parent.childNodes
        if dobrk
            nxt = node
            break
        else if node == obj
            dobrk = true
        
    w.sibling = nxt
    ic = get('innercontents')
    app(ic, obj)
    w.oldStyle = JSON.stringify(obj.style)
    obj.style.width = "100%"
    obj.style.height = "90%"
    obj.style.background = "#EEE"
    obj.style.position = "absolute"
    obj.style.top = "10px"
    obj.style.left = "10px"
    obj.style.zIndex = "2000"
    w.fullscreen = true
    w.reload(true)
    $("html, body").animate({ scrollTop: 0 }, "fast");
    return true

toNormal = (id) ->
    obj = get(id)
    w = findWidget(id)
    
    FSA = get('FS_' + id)
    FSA.innerHTML = "Fullscreen"
    FSA.setAttribute("onclick", "toFullscreen('" + id + "');")
    
    CW = get('CW_' + id)
    CW.setAttribute("onclick", "findWidget('"+id+"').kill();")
    
    if w.sibling
        w.parent.insertBefore(obj, w.sibling)
    else
        app(w.parent, obj)
    obj.style = JSON.parse(w.oldStyle)
    w.fullscreen = false
    w.reload(true)
    return true


updateWidgets = (type, target, eargs) ->
    wargs = window.location.search
    wloc = ""
    for k, v of eargs
        globArgs[k] = v
        g = []
        for k,v of globArgs
                if k and (typeof v != 'undefined' and v != null)
                    g.push(k + '=' + v)
        gargs = "?" + g.join("&")
        wloc = window.location.pathname + gargs
    if wargs != gargs
        window.history.pushState({}, "", wloc);
        console.log("pushed state " + wloc)
        window.onpopstate = (event) ->
            loadPageWidgets()
        
    for widget in widgetCache
        if type == widget.args.type
            widget.args.target = target and target or widget.args.target
            if eargs
                widget.args.eargs = widget.args.eargs and widget.args.eargs or {}
                for k, v of eargs
                    widget.args.eargs[k] = v
                    if (typeof v == 'undefined' or v == null)
                        delete widget.args.eargs[k]
            switch widget.args.type
                when 'donut' then widget.load(donut)
                when 'gauge' then widget.load(gauge)
                when 'radar' then widget.load(radar)
                when 'paragraph' then widget.load(paragraph)
                when 'line' then widget.load(linechart)
                when 'top5' then widget.load(top5)
                when 'factors' then widget.load(factors)
                when 'trends' then widget.load(trend)
                when 'preferences' then widget.load(preferences)
                when 'messages' then widget.load(messages)
                when 'widget' then widget.load(publisher)
                when 'phonebook' then widget.load(phonebook)
                when 'repopicker' then widget.load(explorer)
                when 'sourcepicker' then widget.load(sourceexplorer)
                when 'issuepicker' then widget.load(issueexplorer)
                when 'forumpicker' then widget.load(forumexplorer)
                when 'punchcard' then widget.load(punchcard)
                when 'viewpicker' then widget.load(viewexplorer)
                when 'mailpicker' then widget.load(mailexplorer)
                when 'cipicker' then widget.load(ciexplorer)
                when 'logpicker' then widget.load(logexplorer)
                when 'relationship' then widget.load(relationship)
                when 'treemap' then widget.load(treemap)
                when 'report' then widget.load(report)
                when 'mvp' then widget.load(mvp)
                when 'comstat' then widget.load(comstat)
                when 'worldmap' then widget.load(worldmap)
                when 'jsondump' then widget.load(jsondump)

class pubWidget
    constructor: (@div, @wid, @config) ->
        @args = {}
        fetch("publish/id=" + @wid, {config: @config, widget: this, args: {}}, publisherPublic, null, true)
    inject: (el, clear) ->
        if clear
            @div.innerHTML = ""
        @div.appendChild(el)
        
class Widget
    constructor: (@blocks, @args, pub) ->
        @id = Math.floor(Math.random()*1000000).toString(16)
        
        # Parent object div
        @div = document.createElement('div')
        @div.setAttribute("id", @id)
        @div.setAttribute("class", "x_panel snoot_widget")
        @div.style.float = 'left'
        @json = {}
    
        if (@blocks <= 2) 
            @div.setAttribute("class", "snoot_widget col-md-2 col-sm-4 col-xs-12")
        else if (@blocks <= 3) 
            @div.setAttribute("class", "snoot_widget col-md-3 col-sm-6 col-xs-12")
        else if (@blocks <= 4) 
            @div.setAttribute("class", "snoot_widget col-md-4 col-sm-8 col-xs-12")
        else if (@blocks <= 6) 
            @div.setAttribute("class", "snoot_widget col-md-6 col-sm-12 col-xs-12")
        else if (@blocks <= 9) 
            @div.setAttribute("class", "snoot_widget col-md-9 col-sm-12 col-xs-12")
        else
            @div.setAttribute("class", "snoot_widget col-md-12 col-sm-12 col-xs-12")
        
    
        if not pub
            # Title
            t = document.createElement('div')
            t.setAttribute("class", "x_title")
            tt = document.createElement('h2')
            tt.style.fontSize = "17pt"
            tt.appendChild(document.createTextNode(@args.name))
            t.appendChild(tt)
            
            # Menu 
            ul = document.createElement('ul')
            ul.setAttribute("class", "nav navbar-right panel_toolbox")
            
            # Menu: collapse widget
            li = document.createElement('li')
            @collapse = document.createElement('a')
            @collapse.setAttribute("class", "collapse-link")
            i = document.createElement('i')
            i.setAttribute("class", "fa fa-chevron-up")
            @collapse.appendChild(i)
            li.appendChild(@collapse)
            ul.appendChild(li)
            
            @collapse.addEventListener "click", () ->
                id = this.parentNode.parentNode.parentNode.parentNode.getAttribute("id")
                panel = $('#'+id)
                icon = $(this).find('i')
                content = panel.find('.x_content')
                # fix for some div with hardcoded fix class
                if panel.attr('style')
                    content.slideToggle(200, () ->
                        panel.removeAttr('style')
                        )
                else
                    content.slideToggle(200)
                    panel.css('height', 'auto')
                    
                icon.toggleClass('fa-chevron-up fa-chevron-down');
            
            
            # Menu: remove widget
            li = document.createElement('li')
            a = document.createElement('a')
            a.setAttribute("class", "close-link")
            a.setAttribute("onclick", "findWidget('"+@id+"').kill();")
            i = document.createElement('i')
            i.setAttribute("class", "fa fa-close")
            a.appendChild(i)
            a.setAttribute("id", "CW_" + @id)
            li.appendChild(a)
            ul.appendChild(li)
            
            t.appendChild(ul)
            
            @div.appendChild(t)
            
            cldiv = document.createElement('div')
            cldiv.setAttribute("classs", "clearfix")
            @div.appendChild(cldiv)
        
        @cdiv = document.createElement('div')
        @cdiv.style.width = "100%"
        @cdiv.setAttribute("id", "contents_" + @id)
        @cdiv.setAttribute("class", "x_content")
        @div.appendChild(@cdiv)
        widgetCache.push(this)
        
    cog: (size = 100) ->
        idiv = document.createElement('div')
        idiv.setAttribute("class", "icon")
        idiv.setAttribute("style", "text-align: center; vertical-align: middle; height: 500px;")
        i = new HTML('div', { class: "spinwheel"}, new HTML('div', { class: "spinwheel_md"}, new HTML('div', { class: "spinwheel_sm"})))
        idiv.appendChild(i)
        idiv.appendChild(document.createElement('br'))
        idiv.appendChild(document.createTextNode('Loading, hang on tight..!'))
        @cdiv.innerHTML = ""
        @cdiv.appendChild(idiv)
        
    kill: () ->
        @div.parentNode.removeChild(@div)
    
    inject: (object, clear) ->
        if clear
            @cdiv.innerHTML = ""
            @cdiv.style.textAlign = 'left'
        @cdiv.appendChild(object)
    
    snap: (state) ->
        state.widget.cdiv.innerHTML = "<a style='color: #D44; font-size: 100pt;'><i class='fa fa-warning'></i></a><br/>Oh snap, something went wrong!"
        state.widget.cdiv.style.textAlign = 'center'
    
    load: (callback) ->
        # Insert spinning cog
        this.cog()
        this.callback = callback
        js = @args.eargs
        url = @args.source
        # fetch object and pass on callback
        if @args.type == 'paragraph'
            this.callback(@args, {widget: this, eargs: @args.eargs})
        else
            post(url, js, {widget: this, eargs: @args.eargs}, callback, this.snap)
    reload: (fakeit) ->
        this.cog()
        js = @args.eargs
        url = @args.source
        # fetch object and pass on callback
        if fakeit and this.json
            this.callback(this.json, {widget: this, eargs: @args.eargs})
        else
            post(url, js, {widget: this, eargs: @args.eargs}, this.callback, this.snap)

rowZ = 100
class Row
    constructor: () ->
        @id = Math.floor(Math.random() * 987654321).toString(16)
        @div = document.createElement('div')
        @div.setAttribute("class", "row")
        @div.style.zIndex = rowZ
        rowZ--;
        @div.setAttribute("id", @id)
        @cdiv = document.createElement('div')
        @cdiv.setAttribute("class", "col-md-12")
        @cdiv.setAttribute("id", "contents_" + @id)
        @div.appendChild(@cdiv)
        document.getElementById('innercontents').appendChild(@div)
        
    inject: (object, clear) ->
        @cdiv.innerHTML = "" if clear
        if object instanceof Widget
            @cdiv.appendChild(object.div)
        else
            @cdiv.appendChild(object)
    

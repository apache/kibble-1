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

explorer = (json, state) ->
        
        org = json.organisation
        h = document.createElement('h2')
        if json.tag
            org.name += " (Filter: " + json.tag + ")"
        h.appendChild(document.createTextNode("Exploring " + org.name + ":"))
        state.widget.inject(h, true)
        list = document.createElement('select')
        state.widget.inject(list)
        opt = document.createElement('option')
        opt.value = ""
        slen = 0
        for item in json.sources
            if item.type in ['git', 'svn', 'gerrit', 'github'] and item.noclone != true
                slen++
        opt.text = "All " + slen + " repositories"
        list.appendChild(opt)
        json.sources.sort((a,b) ->
            return if (a.sourceURL == b.sourceURL) then 0 else (if a.sourceURL > b.sourceURL then 1 else -1)
            )
        for item in json.sources
            if item.type in ['git', 'svn', 'gerrit', 'github'] and item.noclone != true
                opt = document.createElement('option')
                opt.value = item.sourceID
                ezURL = null
                m = item.sourceURL.match(/^([a-z]+:\/\/.+?)[\/?]([^\/?]+)$/i)
                if m and m.length == 3
                    ezURL = "#{m[2]} - (#{m[1]})"
                opt.text = if ezURL then ezURL else item.sourceURL
                if globArgs.source and globArgs.source == item.sourceID
                    opt.selected = 'selected'
                list.appendChild(opt)
        
        ID = Math.floor(Math.random() * 987654321).toString(16)
        list.setAttribute('id', ID)
        $("#"+ID).chosen().change(() ->
                source = this.value
                
                if source == ""
                        source = null
                globArgs.source = source
                updateWidgets('donut', null, { source: source })
                updateWidgets('gauge', null, { source: source })
                updateWidgets('line', null, { source: source })
                updateWidgets('contacts', null, { source: source })
                updateWidgets('top5', null, { source: source })
                updateWidgets('factors', null, { source: source })
                updateWidgets('trends', null, { source: source })
                updateWidgets('mvp', null, { source: source })
                updateWidgets('comstat', null, { source: source })
                updateWidgets('jsondump', null, { source: source })
              )
        
        
        
        # Unique commits label
        id = Math.floor(Math.random() * 987654321).toString(16)
        chk = document.createElement('input')
        chk.setAttribute("type", "checkbox")
        chk.setAttribute("id", id)
        chk.style.marginLeft = '10px'
        if globArgs.author and globArgs.author == 'true'
                chk.checked = true
        chk.addEventListener("change", () ->
                unique = null
                if this.checked
                        author = 'true'
                        globArgs['author'] = 'true'
                
                updateWidgets('donut', null, { author: author })
                updateWidgets('gauge', null, { author: author })
                updateWidgets('line', null, { author: author })
                updateWidgets('contacts', null, { author: author })
                updateWidgets('top5', null, { author: author })
                updateWidgets('factors', null, { author: author })
                updateWidgets('trends', null, { author: author })
                updateWidgets('relationship', null, {author: author})
                updateWidgets('mvp', null, {author: author})
                updateWidgets('comstat', null, { author: author })
                updateWidgets('jsondump', null, { author: author })
                )
        state.widget.inject(chk)
        label = document.createElement('label')
        label.setAttribute("for", id)
        label.setAttribute("title", "Check this box to authorships instead of committerships")
        chk.setAttribute("title", "Check this box to authorships instead of committerships")
        label.style.paddingLeft = '5px'
        label.appendChild(document.createTextNode('Show authors'))
        state.widget.inject(label)


sourceexplorer = (json, state) ->
        
        org = json.organisation
        h = document.createElement('h4')
        if json.tag
            org.name += " (Filter: " + json.tag + ")"
        h.appendChild(document.createTextNode("Exploring " + org.name + ":"))
        state.widget.inject(h, true)
        div = new HTML('div', {class: "form-group"})
        list = new HTML('select', { class: "form-control"})
        div.inject(list)
        state.widget.inject(div)
        opt = document.createElement('option')
        opt.value = ""
        slen = 0
        for item in json.sources
                slen++
        opt.text = "All " + slen + " sources"
        list.appendChild(opt)
        json.sources.sort((a,b) ->
            return if (a.sourceURL == b.sourceURL) then 0 else (if a.sourceURL > b.sourceURL then 1 else -1)
            )
        for item in json.sources
            if true
                opt = document.createElement('option')
                opt.value = item.sourceID
                ezURL = null
                m = item.sourceURL.match(/^([a-z]+:\/\/.+?)[\/?]([^\/?]+)$/i)
                if m and m.length == 3
                    ezURL = "#{m[2]} - (#{m[1]})"
                opt.text = if ezURL then ezURL else item.sourceURL
                if globArgs.source and globArgs.source == item.sourceID
                    opt.selected = 'selected'
                list.appendChild(opt)
                
        ID = Math.floor(Math.random() * 987654321).toString(16)
        list.setAttribute('id', ID)
        $("#"+ID).chosen().change(() ->
                source = this.value
                
                if source == ""
                        source = null
                globArgs.source = source
                updateWidgets('donut', null, { source: source })
                updateWidgets('gauge', null, { source: source })
                updateWidgets('line', null, { source: source })
                updateWidgets('contacts', null, { source: source })
                updateWidgets('top5', null, { source: source })
                updateWidgets('factors', null, { source: source })
                updateWidgets('trends', null, { source: source })
                updateWidgets('mvp', null, { source: source })
                updateWidgets('comstat', null, { source: source })
                updateWidgets('jsondump', null, { author: author })
        )



mailexplorer = (json, state) ->
        
        org = json.organisation
        h = document.createElement('h4')
        if json.tag
            org.name += " (Filter: " + json.tag + ")"
        h.appendChild(document.createTextNode("Exploring " + org.name + ":"))
        
        state.widget.inject(h, true)
        list = document.createElement('select')
        state.widget.inject(list)
        opt = document.createElement('option')
        opt.value = ""
        slen = 0
        for item in json.sources
            if item.type in ['mail', 'ponymail', 'pipermail', 'hyperkitty']
                slen++
        opt.text = "All " + slen + " mailing lists"
        list.appendChild(opt)
        json.sources.sort((a,b) ->
            return if (a.sourceURL == b.sourceURL) then 0 else (if a.sourceURL > b.sourceURL then 1 else -1)
            )
        for item in json.sources
            if item.type in ['mail', 'ponymail', 'pipermail', 'hyperkitty']
                opt = document.createElement('option')
                opt.value = item.sourceID
                ezURL = null
                m = item.sourceURL.match(/^([a-z]+:\/\/.+?)[\/?]([^\/?]+)$/i)
                if m and m.length == 3
                    ezURL = "#{m[2]} - (#{m[1]})"
                opt.text = if ezURL then ezURL else item.sourceURL
                if globArgs.source and globArgs.source == item.sourceID
                    opt.selected = 'selected'
                list.appendChild(opt)
        
        ID = Math.floor(Math.random() * 987654321).toString(16)
        list.setAttribute('id', ID)
        $("#"+ID).chosen().change(() ->
                source = this.value
                
                if source == ""
                        source = null
                globArgs.source = source
                updateWidgets('donut', null, { source: source })
                updateWidgets('gauge', null, { source: source })
                updateWidgets('line', null, { source: source })
                updateWidgets('contacts', null, { source: source })
                updateWidgets('top5', null, { source: source })
                updateWidgets('factors', null, { source: source })
                updateWidgets('trends', null, { source: source })
                updateWidgets('relationship', null, { source: source })
                
        )
        
logexplorer = (json, state) ->
        
        org = json.organisation
        h = document.createElement('h4')
        if json.tag
            org.name += " (Filter: " + json.tag + ")"
        h.appendChild(document.createTextNode("Exploring " + org.name + ":"))
        
        state.widget.inject(h, true)
        list = document.createElement('select')
        state.widget.inject(list)
        opt = document.createElement('option')
        opt.value = ""
        slen = 0
        for item in json.sources
            if item.type == 'stats'
                slen++
        opt.text = "All " + slen + " log files"
        list.appendChild(opt)
        json.sources.sort((a,b) ->
            return if (a.sourceURL == b.sourceURL) then 0 else (if a.sourceURL > b.sourceURL then 1 else -1)
            )
        for item in json.sources
            if item.type == 'stats'
                opt = document.createElement('option')
                opt.value = item.sourceID
                ezURL = null
                m = item.sourceURL.match(/^([a-z]+:\/\/.+?)[\/?]([^\/?]+)$/i)
                if m and m.length == 3
                    ezURL = "#{m[2]} - (#{m[1]})"
                opt.text = if ezURL then ezURL else item.sourceURL
                if globArgs.source and globArgs.source == item.sourceID
                    opt.selected = 'selected'
                list.appendChild(opt)
        
        ID = Math.floor(Math.random() * 987654321).toString(16)
        list.setAttribute('id', ID)
        $("#"+ID).chosen().change(() ->
                source = this.value
                
                if source == ""
                        source = null
                globArgs.source = source
                updateWidgets('donut', null, { source: source })
                updateWidgets('gauge', null, { source: source })
                updateWidgets('line', null, { source: source })
                updateWidgets('worldmap', null, { source: source })
                updateWidgets('top5', null, { source: source })
                updateWidgets('factors', null, { source: source })
                updateWidgets('trends', null, { source: source })
                
        )
        
issueexplorer = (json, state) ->
        
        org = json.organisation
        if json.tag
            org.name += " (Filter: " + json.tag + ")"
        h = document.createElement('h4')
        h.appendChild(document.createTextNode("Exploring " + org.name + ":"))
        state.widget.inject(h, true)
        list = document.createElement('select')
        state.widget.inject(list)
        opt = document.createElement('option')
        opt.value = ""
        slen = 0
        for item in json.sources
            if item.type in ['jira', 'gerrit', 'github', 'bugzilla']
                slen++
        opt.text = "All " + slen + " issue tracker(s)"
        list.appendChild(opt)
        json.sources.sort((a,b) ->
            return if (a.sourceURL == b.sourceURL) then 0 else (if a.sourceURL > b.sourceURL then 1 else -1)
            )
        for item in json.sources
            if item.type in ['jira', 'gerrit', 'github', 'bugzilla']
                opt = document.createElement('option')
                opt.value = item.sourceID
                ezURL = null
                n = item.sourceURL.match(/^([a-z]+:\/\/.+?)\/([-.A-Z0-9]+)$/i)                
                m = item.sourceURL.match(/^([a-z]+:\/\/.+?)\s(.+)$/i)
                if n and n.length == 3
                    ezURL = "#{n[2]} - (#{n[1]})"
                else if m and m.length == 3
                    ezURL = "#{m[2]} - (#{m[1]})"
                opt.text = if ezURL then ezURL else item.sourceURL
                if globArgs.source and globArgs.source == item.sourceID
                    opt.selected = 'selected'
                list.appendChild(opt)
        
        ID = Math.floor(Math.random() * 987654321).toString(16)
        list.setAttribute('id', ID)
        $("#"+ID).chosen().change(() ->
                source = this.value
                
                if source == ""
                        source = null
                globArgs.source = source
                updateWidgets('donut', null, { source: source })
                updateWidgets('gauge', null, { source: source })
                updateWidgets('line', null, { source: source })
                updateWidgets('contacts', null, { source: source })
                updateWidgets('top5', null, { source: source })
                updateWidgets('factors', null, { source: source })
                updateWidgets('trends', null, { source: source })
                
        )
        


forumexplorer = (json, state) ->
        
        org = json.organisation
        if json.tag
            org.name += " (Filter: " + json.tag + ")"
        h = document.createElement('h4')
        h.appendChild(document.createTextNode("Exploring " + org.name + ":"))
        state.widget.inject(h, true)
        list = document.createElement('select')
        state.widget.inject(list)
        opt = document.createElement('option')
        opt.value = ""
        slen = 0
        for item in json.sources
            if item.type in ['forum', 'discourse', 'askbot']
                slen++
        opt.text = "All " + slen + " forum(s)"
        list.appendChild(opt)
        json.sources.sort((a,b) ->
            return if (a.sourceURL == b.sourceURL) then 0 else (if a.sourceURL > b.sourceURL then 1 else -1)
            )
        for item in json.sources
            if item.type in ['forum', 'discourse', 'askbot']
                opt = document.createElement('option')
                opt.value = item.sourceID
                ezURL = null
                n = item.sourceURL.match(/^([a-z]+:\/\/.+?)\/([-.A-Z0-9]+)$/i)                
                m = item.sourceURL.match(/^([a-z]+:\/\/.+?)\s(.+)$/i)
                if n and n.length == 3
                    ezURL = "#{n[2]} - (#{n[1]})"
                else if m and m.length == 3
                    ezURL = "#{m[2]} - (#{m[1]})"
                opt.text = if ezURL then ezURL else item.sourceURL
                if globArgs.source and globArgs.source == item.sourceID
                    opt.selected = 'selected'
                list.appendChild(opt)
        
        ID = Math.floor(Math.random() * 987654321).toString(16)
        list.setAttribute('id', ID)
        $("#"+ID).chosen().change(() ->
                source = this.value
                
                if source == ""
                        source = null
                globArgs.source = source
                updateWidgets('donut', null, { source: source })
                updateWidgets('gauge', null, { source: source })
                updateWidgets('line', null, { source: source })
                updateWidgets('contacts', null, { source: source })
                updateWidgets('top5', null, { source: source })
                updateWidgets('factors', null, { source: source })
                updateWidgets('trends', null, { source: source })
                
        )
        


imexplorer = (json, state) ->
        
        org = json.organisation
        if json.tag
            org.name += " (Filter: " + json.tag + ")"
        h = document.createElement('h4')
        h.appendChild(document.createTextNode("Exploring " + org.name + ":"))
        state.widget.inject(h, true)
        list = document.createElement('select')
        state.widget.inject(list)
        opt = document.createElement('option')
        opt.value = ""
        slen = 0
        for item in json.sources
            if item.type in ['irc','gitter']
                slen++
        opt.text = "All " + slen + " messaging sources"
        list.appendChild(opt)
        json.sources.sort((a,b) ->
            return if (a.sourceURL == b.sourceURL) then 0 else (if a.sourceURL > b.sourceURL then 1 else -1)
            )
        for item in json.sources
            if item.type in ['irc', 'gitter']
                opt = document.createElement('option')
                opt.value = item.sourceID
                ezURL = null
                n = item.sourceURL.match(/^([a-z]+:\/\/.+?)\/([#\S+]+)$/i)                
                m = item.sourceURL.match(/^([a-z]+:\/\/.+?)\s(.+)$/i)
                if n and n.length == 3
                    ezURL = "#{n[2]} - (#{n[1]})"
                else if m and m.length == 3
                    ezURL = "#{m[2]} - (#{m[1]})"
                opt.text = if ezURL then ezURL else item.sourceURL
                if globArgs.source and globArgs.source == item.sourceID
                    opt.selected = 'selected'
                list.appendChild(opt)
        
        ID = Math.floor(Math.random() * 987654321).toString(16)
        list.setAttribute('id', ID)
        $("#"+ID).chosen().change(() ->
                source = this.value
                
                if source == ""
                        source = null
                globArgs.source = source
                updateWidgets('donut', null, { source: source })
                updateWidgets('gauge', null, { source: source })
                updateWidgets('line', null, { source: source })
                updateWidgets('contacts', null, { source: source })
                updateWidgets('top5', null, { source: source })
                updateWidgets('factors', null, { source: source })
                updateWidgets('trends', null, { source: source })
                
        , false)
        $('select').chosen();
        

ciexplorer = (json, state) ->
        
        org = json.organisation
        if json.tag
            org.name += " (Filter: " + json.tag + ")"
        h = document.createElement('h4')
        h.appendChild(document.createTextNode("Exploring " + org.name + ":"))
        state.widget.inject(h, true)
        list = document.createElement('select')
        state.widget.inject(list)
        opt = document.createElement('option')
        opt.value = ""
        slen = 0
        for item in json.sources
            if item.type in ['jenkins','travis','buildbot']
                slen++
        opt.text = "All " + slen + " CI Services"
        list.appendChild(opt)
        json.sources.sort((a,b) ->
            return if (a.sourceURL == b.sourceURL) then 0 else (if a.sourceURL > b.sourceURL then 1 else -1)
            )
        for item in json.sources
            if item.type in ['jenkins','travis','buildbot']
                opt = document.createElement('option')
                opt.value = item.sourceID
                ezURL = null
                n = item.sourceURL.match(/^([a-z]+:\/\/.+?)\/([#\S+]+)$/i)                
                m = item.sourceURL.match(/^([a-z]+:\/\/.+?)\s(.+)$/i)
                if n and n.length == 3
                    ezURL = "#{n[2]} - (#{n[1]})"
                else if m and m.length == 3
                    ezURL = "#{m[2]} - (#{m[1]})"
                opt.text = if ezURL then ezURL else item.sourceURL
                if globArgs.source and globArgs.source == item.sourceID
                    opt.selected = 'selected'
                list.appendChild(opt)
        
        ID = Math.floor(Math.random() * 987654321).toString(16)
        list.setAttribute('id', ID)
        $("#"+ID).chosen().change(() ->
                source = this.value
                
                if source == ""
                        source = null
                globArgs.source = source
                updateWidgets('donut', null, { source: source })
                updateWidgets('gauge', null, { source: source })
                updateWidgets('line', null, { source: source })
                updateWidgets('contacts', null, { source: source })
                updateWidgets('top5', null, { source: source })
                updateWidgets('factors', null, { source: source })
                updateWidgets('trends', null, { source: source })
                updateWidgets('relationship', null, { source: source })
                
        )
        

multiviewexplorer = (json, state) ->
        org = json.organisation
        h = document.createElement('h4')
        h.appendChild(document.createTextNode("Select views to compare:"))
        state.widget.inject(h, true)
        for k in [1..3]
            tName = 'tag'+k
            list = document.createElement('select')
            list.setAttribute("data", tName)
            state.widget.inject(list)
            opt = document.createElement('option')
            opt.value = ""
            opt.text = "(None)"
            list.appendChild(opt)
            opt = document.createElement('option')
            opt.value = "---"
            opt.text = "Entire organisation"
            if globArgs[tName] and globArgs[tName] == '---'
                opt.selected = 'selected'
            list.appendChild(opt)
            if isArray(json.views)
                json.views.sort((a,b) ->
                    return if (a.name == b.name) then 0 else (if a.name > b.name then 1 else -1)
                    )
            for item in json.views
                opt = document.createElement('option')
                opt.value = item.id
                opt.text = item.name
                if globArgs[tName] and globArgs[tName] == item.id
                    opt.selected = 'selected'
                list.appendChild(opt)
            
                ID = Math.floor(Math.random() * 987654321).toString(16)
                list.setAttribute('id', ID)
                $("#"+ID).chosen().change(() ->
                    source = this.value
                    if source == ""
                            source = null
                    tName = this.getAttribute("data")
                    globArgs[tName] = source
                    x = {}
                    x[tName] = source
                    updateWidgets('donut', null, x)
                    updateWidgets('gauge', null, x)
                    updateWidgets('line', null, x)
                    updateWidgets('contacts', null, x)
                    updateWidgets('top5', null, x)
                    updateWidgets('factors', null, x)
                    updateWidgets('trends', null, x)
                    updateWidgets('radar', null, x)
              )
        
subFilterGlob = null
subFilter = () ->
        source = subFilterGlob
        if source == ""
                source = null
        tName = 'subfilter'
        globArgs[tName] = source
        x = {}
        x[tName] = source
        updateWidgets('sourcepicker', null, x)
        updateWidgets('repopicker', null, x)
        updateWidgets('issuepicker', null, x)
        updateWidgets('forumpicker', null, x)
        updateWidgets('mailpicker', null, x)
        updateWidgets('logpicker', null, x)
        updateWidgets('donut', null, x)
        updateWidgets('gauge', null, x)
        updateWidgets('line', null, x)
        updateWidgets('contacts', null, x)
        updateWidgets('top5', null, x)
        updateWidgets('factors', null, x)
        updateWidgets('trends', null, x)
        updateWidgets('radar', null, x)
        updateWidgets('widget', null, x)
        updateWidgets('relationship', null, x)
        updateWidgets('treemap', null, x)
        updateWidgets('report', null, x)
        updateWidgets('mvp', null, x)
        updateWidgets('comstat', null, x)
        updateWidgets('worldmap', null, x)
        updateWidgets('jsondump', null, x)
        
        $( "a" ).each( () ->
            url = $(this).attr('href')
            if url
                m = url.match(/^(.+\?page=[-a-z]+.*?)(?:&subfilter=[^&]+)?(.*)$/)
                if m
                    if source
                            $(this).attr('href', "#{m[1]}&subfilter=#{source}#{m[2]}")
                    else
                            $(this).attr('href', "#{m[1]}#{m[2]}")
        )
        

viewexplorer = (json, state) ->
        org = json.organisation
        h = document.createElement('h4')
        h.appendChild(document.createTextNode("Select a view to use:"))
        state.widget.inject(h, true)
        tName = 'view'
        list = document.createElement('select')
        list.setAttribute("data", tName)
        state.widget.inject(list)
        opt = document.createElement('option')
        opt.value = ""
        opt.text = "(None)"
        list.appendChild(opt)
        opt = document.createElement('option')
        opt.value = "---"
        opt.text = "Entire organisation"
        if globArgs[tName] and globArgs[tName] == '---'
            opt.selected = 'selected'
        list.appendChild(opt)
        if isArray(json.views)
            json.views.sort((a,b) ->
                return if (a.name == b.name) then 0 else (if a.name > b.name then 1 else -1)
                )
        for item in json.views
            opt = document.createElement('option')
            opt.value = item.id
            opt.text = item.name
            if globArgs[tName] and globArgs[tName] == item.id
                opt.selected = 'selected'
            list.appendChild(opt)
        
        ID = Math.floor(Math.random() * 987654321).toString(16)
        list.setAttribute('id', ID)
        $("#"+ID).chosen().change(() ->
                source = this.value
                if source == ""
                        source = null
                tName = this.getAttribute("data")
                globArgs[tName] = source
                x = {}
                x[tName] = source
                updateWidgets('sourcepicker', null, x)
                updateWidgets('repopicker', null, x)
                updateWidgets('issuepicker', null, x)
                updateWidgets('mailpicker', null, x)
                updateWidgets('logpicker', null, x)
                updateWidgets('donut', null, x)
                updateWidgets('gauge', null, x)
                updateWidgets('line', null, x)
                updateWidgets('contacts', null, x)
                updateWidgets('top5', null, x)
                updateWidgets('factors', null, x)
                updateWidgets('trends', null, x)
                updateWidgets('radar', null, x)
                updateWidgets('widget', null, x)
                updateWidgets('relationship', null, x)
                updateWidgets('treemap', null, x)
                updateWidgets('report', null, x)
                updateWidgets('mvp', null, x)
                updateWidgets('comstat', null, x)
                updateWidgets('worldmap', null, x)
                updateWidgets('jsondump', null, x)
                
                $( "a" ).each( () ->
                    url = $(this).attr('href')
                    if url
                        m = url.match(/^(.+\?page=[-a-z]+)(?:&view=[a-f0-9]+)?(.*)$/)
                        if m
                            if source
                                    $(this).attr('href', "#{m[1]}&view=#{source}#{m[2]}")
                            else
                                    $(this).attr('href', "#{m[1]}#{m[2]}")
                )
                
        )
        
        # Quick filter
        state.widget.inject(new HTML('br'))
        i = new HTML('input', {id:'subfilter', size: 16, type: 'text', value: globArgs.subfilter, onChange: 'subFilterGlob = this.value;', placeholder: 'sub-filter'})
        b = new HTML('input', {style: { marginLeft: '10px'}, class: 'btn btn-small btn-success', type: 'button', onClick: 'subFilter();', value: "sub-filter"})
        rb = new HTML('input', {style: { marginLeft: '10px'}, class: 'btn btn-small btn-danger', type: 'button', onClick: 'get("subfilter").value=""; subFilterGlob=""; subFilter();', value: "reset"})
        state.widget.inject(i)
        state.widget.inject(b)
        state.widget.inject(rb)
        
        if globArgs.subfilter and globArgs.subfilter.length > 0
                source = globArgs.subfilter
                $( "a" ).each( () ->
                        url = $(this).attr('href')
                        if url
                            m = url.match(/^(.+\?page=[-a-z]+.*?)(?:&subfilter=[a-f0-9]+)?(.*)$/)
                            if m
                                if source
                                        $(this).attr('href', "#{m[1]}&subfilter=#{source}#{m[2]}")
                                else
                                        $(this).attr('href', "#{m[1]}#{m[2]}")
                    )
        
        if globArgs.email
                div = new HTML('div', {}, "Currently filtering results based on " + globArgs.email + ". - ")
                div.inject(new HTML('a', { href: 'javascript:void(filterPerson(null));'}, "Reset filter"))
                state.widget.inject(div)
            
        

widgetexplorer = (json, state) ->
        pwidgets = {
            'languages': 'Code: Language breakdown',
            'commit-history-year': "Code: Commit history (past year)"
            'commit-history-all': "Code: Commit history (all time)"
            'commit-top5-year': "Code: top 5 committers (past year)"
            'commit-top5-all': "Code: top 5 committers (all time)"
            'committer-count-year': "Code: Committers/Authors per month (past year)"
            'committer-count-all': "Code: Committers/Authors per month (all time)"
            'commit-lines-year': "Code: Lines changed (past year)"
            'commit-lines-all': "Code: Lines changed (all time)"
            'sloc-map': "Code: Language Treemap"
            'repo-size-year': "Repos: top 15 by lines of code"
            'repo-commits-year': "Repos: top 15 by number of commits (past year)"
            'repo-commits-all': "Repos: top 15 by number of commits (all time)"
            'evolution': "Code: Code evolution (all time)"
            'evolution-extended': "Code: Code evolution (individual languages, all time)"
            'issue-count-year': "Issues: Tickets opened/closed (past year)"
            'issue-count-all': "Issues: Tickets opened/closed (all time)"
            'issue-operators-year': "Issues: Ticket creators/closers (past year)"
            'issue-operators-all': "Issues: Ticket creators/closers (all time)"
            'issue-queue-all': "Issue queue size by ticket age"
            'email-count-year': "Mail: Emails/threads/authors (past year)"
            'email-count-all': "Mail: Emails/threads/authors (all time)"
            'im-stats-year': "Online messaging activity (past year)",
            'im-stats-all': "Online messaging activity (all time)",
            'compare-commits-year': "Commits by Affiliation (past year)",
            'compare-commits-all': "Commits by Affiliation (all time)"
            'repo-relationship-year': "Repository relationships (past year)"
            'repo-relationship-2year': "Repository relationships (past two years)"
            'issue-relationship-year': "Issue tracker relationships (past year)"
            'issue-relationship-2year': "Issue tracker relationships (past two years)"
            'log-stats-year': "Downloads/Visits (past year)"
            'log-stats-all': "Downloads/Visits (all time)"
            'log-map-month': "Downloads/Visits per country (past month)"
            'log-map-year': "Downloads/Visits per country (past year)"
            'log-map-all': "Downloads/Visits per country (all time)"
        }
        org = json.organisation
        h = document.createElement('h4')
        h.appendChild(document.createTextNode("Select a widget to use:"))
        state.widget.inject(h, true)
        tName = 'widget'
        list = document.createElement('select')
        list.setAttribute("data", tName)
        state.widget.inject(list)
        opt = document.createElement('option')
        opt.value = ""
        opt.text = "Select a widget type:"
        list.appendChild(opt)
        for key, value of pwidgets
            opt = document.createElement('option')
            opt.value = key
            opt.text = value
            if globArgs[tName] and globArgs[tName] == key
                opt.selected = 'selected'
            list.appendChild(opt)
        
        list.addEventListener("change", () ->
                source = this.value
                if source == ""
                        source = null
                tName = this.getAttribute("data")
                globArgs[tName] = source
                x = {}
                x[tName] = source
                updateWidgets('widget', null, x)
                updateWidgets('donut', null, x)
                updateWidgets('gauge', null, x)
                updateWidgets('line', null, x)
                updateWidgets('contacts', null, x)
                updateWidgets('top5', null, x)
                updateWidgets('factors', null, x)
                updateWidgets('trends', null, x)
                updateWidgets('radar', null, x)
                
        , false)
            
        

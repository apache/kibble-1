addsources = (form) ->
    rv = get('retval')
    cog(rv)
    json = {
        action: 'bulkadd',
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
            password: form.apass.value
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
    postJSON('manage-sources', json, null, sourceret)
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
        postJSON('manage-sources', { action: 'delete', source: hash }, null, null)
        
tagsource = (hash) ->
    tag = window.prompt("Please enter the tag with which you wish to associate this source, or type nothing to untag.")
    if tag == ""
        tag = null
    tr = get(hash)
    postJSON('manage-sources', { action: 'tag', source: hash, tag: tag }, null, null)

sourcelist = (json, state) ->
    
    slist = mk('div')
    for org, sources of json.sources
        h1 = mk('h1')
        app(h1, txt(org+":"))
        app(slist, h1)
        
        tbl = mk('table')
        set(tbl, 'class', 'table table-striped')
        thead = mk('thead')
        tr = mk('tr')
        for el in ['Type', 'Source', 'Tag(s)', 'Progress', 'Last Update',  'Status', 'Actions']
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
        
        tbody = mk('tbody')
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
            
            d = mk('tr')
            set(d, 'id', source.sourceID)
            set(d, 'scope', 'row')
            tt = mk('td')
            app(tt, txt(source.type))
            set(tt, 'data-source-type', source.type)
            app(d, tt)
            
            t = mk('td')
            t.style.color = "#369"
            app(t, txt(source.sourceURL))
            app(d, t)
            
            t = mk('td')
            t.style.color = "#369"
            app(t, txt(source.tag || ""))
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
                
            t = mk('td')
            borked = false
            steps = ['sync', 'census', 'count', 'evolution']
            if source.type == 'mail'
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
            
            # tag a source
            dbtn = mk('button')
            set(dbtn, 'class', 'btn btn-info')
            set(dbtn, 'onclick', 'tagsource("' + source.sourceID + '");')
            dbtn.style.padding = "2px"
            app(dbtn, txt("Tag"))
            app(act, dbtn)
            app(d, act)
            
            app(tbody, d)
        app(tbl, tbody)
    app(slist, tbl)
    state.widget.inject(slist, true)
    
    
    retval = mk('div')
    set(retval, 'id', 'retval')
    state.widget.inject(retval)
    
    form = mk('form')
    set(form, 'onsubmit', 'return addsources(this);')
    fs = mk('fieldset')
    lg = mk('legend')
    app(lg, txt('Bulk add new sources:'))
    app(fs, lg)
    
    
    # source type
    stype = mk('div')
    set(stype, 'class', 'form-group')
    stypelabel = mk('label')
    set(stypelabel, 'class', 'control-label col-md-3 col-sm-3 col-xs-12')
    app(stypelabel, txt('Source type: '))
    app(stype, stypelabel)
    stypediv = mk('div')
    set(stypediv, 'class', 'ol-md-3 col-sm-3 col-xs-6')
    stypeinput = mk('select')
    set(stypeinput, 'name', 'stype')
    set(stypeinput, 'class', 'form-control')
    types = ['auto', 'git', 'svn', 'mail', 'github', 'gerrit', 'jira', 'bugzilla', 'stats', 'irc']
    for type in types
        opt = mk('option')
        opt.text = type
        opt.value = type
        app(stypeinput, opt)
    app(stypediv, stypeinput)
    app(stype, stypediv)
    app(fs, stype)
    app(fs, txt("Snoot will try to automatically determine the source type for each source. You may also specify a specific type if you like."))
    cf = mk('div')
    set(cf, 'class', 'clearfix')
    app(fs, cf)
    
    div = mk('div')
    label = mk('label')
    sw = mk('input')
    set(sw, 'type', 'checkbox')
    set(sw, 'name', 'auth')
    set(sw, 'class', 'js-switch')
    app(label, sw)
    app(label, txt('Authorization required'))
    app(div, label)
    swi(sw)
    
    # Authorization stuff
    auth = mk('div')
    set(auth, 'class', 'col-md-3 col-sm-3 col-xs-12')
    auth.style.display = 'none'
    h2 = mk('h2')
    app(h2, txt("Authorization settings:"))
    app(auth, h2)
    
    # Auth type
    atype = mk('div')
    set(atype, 'class', 'form-group')
    atypelabel = mk('label')
    set(atypelabel, 'class', 'control-label col-md-3 col-sm-3 col-xs-12')
    app(atypelabel, txt('Authorization type: '))
    app(atype, atypelabel)
    atypediv = mk('div')
    set(atypediv, 'class', 'ol-md-3 col-sm-3 col-xs-6')
    atypeinput = mk('select')
    set(atypeinput, 'name', 'atype')
    set(atypeinput, 'class', 'form-control')
    types = ['basic', 'gerrit', 'jira']
    for type in types
        opt = mk('option')
        opt.text = type
        opt.value = type
        app(atypeinput, opt)
    app(atypediv, atypeinput)
    app(atype, atypediv)
    app(auth, atype)
    cf = mk('div')
    set(cf, 'class', 'clearfix')
    app(auth, cf)
    
    
    # Auth username
    auser = mk('div')
    set(auser, 'class', 'form-group')
    auserlabel = mk('label')
    set(auserlabel, 'class', 'control-label col-md-3 col-sm-3 col-xs-12')
    app(auserlabel, txt('Username: '))
    app(auser, auserlabel)
    auserdiv = mk('div')
    set(auserdiv, 'class', 'ol-md-3 col-sm-3 col-xs-6')
    auserinput = mk('input')
    set(auserinput, 'class', 'form-control')
    set(auserinput, 'placeholder', 'none, basic, gerrit')
    set(auserinput, 'name', 'auser')
    app(auserdiv, auserinput)
    app(auser, auserdiv)
    app(auth, auser)
    cf = mk('div')
    set(cf, 'class', 'clearfix')
    app(auth, cf)
    
    # Auth password
    apass = mk('div')
    set(apass, 'class', 'form-group')
    apasslabel = mk('label')
    set(apasslabel, 'class', 'control-label col-md-3 col-sm-3 col-xs-12')
    app(apasslabel, txt('Password: '))
    app(apass, apasslabel)
    apassdiv = mk('div')
    set(apassdiv, 'class', 'ol-md-3 col-sm-3 col-xs-6')
    apassinput = mk('input')
    set(apassinput, 'class', 'form-control')
    set(apassinput, 'placeholder', 'none, basic, gerrit')
    set(apassinput, 'name', 'apass')
    app(apassdiv, apassinput)
    app(apass, apassdiv)
    app(auth, apass)
    
    
    app(fs, div)
    app(fs, auth)
    cf = mk('div')
    set(cf, 'class', 'clearfix')
    app(fs, cf)
    
    div2 = mk('div')
    label2 = mk('label')
    sw2 = mk('input')
    set(sw2, 'type', 'checkbox')
    set(sw2, 'name', 'noclone')
    set(sw2, 'class', 'js-switch')
    
    app(label2, sw2)
    app(label2, txt('Issues only, no clone'))
    app(div2, label2)
    app(fs, div2)
    swi(sw2)
    
    
    cf = mk('div')
    set(cf, 'class', 'clearfix')
    app(fs, cf)
    
    
    # Source list
    slist = mk('div')
    set(slist, 'class', 'form-group')
    slistlabel = mk('label')
    set(slistlabel, 'class', 'control-label col-md-3 col-sm-3 col-xs-12')
    app(slistlabel, txt('Source list: '))
    app(slist, slistlabel)
    slistdiv = mk('div')
    set(slistdiv, 'class', 'ol-md-3 col-sm-3 col-xs-6')
    slistinput = mk('textarea')
    slistinput.style.height = "200px"
    set(slistinput, 'placeholder', 'One source per line')
    set(slistinput, 'name', 'sources')
    set(slistinput, 'class', 'form-control')
    app(slistdiv, slistinput)
    a = mk('a')
    set(a, 'href', 'sources.html')
    set(a, 'target', '_blank')
    app(a, txt("How do I specify sources?"))
    app(slistdiv, a)
    app(slist, slistdiv)
    app(fs, slist)
    cf = mk('div')
    set(cf, 'class', 'clearfix')
    app(fs, cf)
    
    btn = mk('input')
    set(btn, 'type', 'submit')
    set(btn, 'value', 'Add sources')
    app(fs, btn)
    app(form, fs)
    
    sw.addEventListener('click', () ->
        if this.checked
            auth.style.display = 'block'
        else
            auth.style.display = 'none'
        )
    state.widget.inject(form)
    
    
tagList = {}

affiliation = (json, state) ->
    obj = mk('div')
    groups = []
    for group, members of json.groups
        groups.push(group)
    groups.sort((a,b) => json.groups[b].length - json.groups[a].length)
    h3 = mk('h3')
    ngroups = groups.length
    if '_untagged' in groups
        ngroups--
    app(h3, txt("Found " + ngroups + " organisations/companies:"))
    app(obj, h3)
    
    btn = mk('input')
    set(btn, 'type', 'button')
    set(btn, 'class', 'btn btn-info')
    set(btn, 'value', 'Group wizard')
    set(btn, 'widget', state.widget.id)
    btn.addEventListener("click", () ->
        w = findWidget(this.getAttribute('widget'))
        w.args.eargs = {
            autogroup: true
        }
        w.callback = affiliationWizard
        w.reload()
    )
    
    p = mk('p')
    app(p, txt("You may use the "))
    app(p, btn)
    app(p, txt(" to quickly group people into companies etc."))
    app(obj, p)
    p = mk('p')
    app(p, txt("NOTE: For certain charts (evolutions etc), only the 30 largest groups will be shown due to computational optimisations."))
    app(obj, p)
    for group in groups
        groupname = group.split(/\./)[0].replace(/^([a-z])/, (a) => a.toUpperCase())
        if group == '_untagged'
            groupname = "People with no current affiliation"
        h4 = mk('h4')
        app(h4, txt(groupname + ": " + json.groups[group].length + " members"))
        h4.style.fontSize = "14pt"
        h4.setAttribute("onclick", "var a = get('people_" + group + "'); a.style.display = (a.style.display == 'block') ? 'none' : 'block';")
        h4.style.display = "inline-block"
        h4.style.cursor = 'se-resize'
        app(obj, h4)
        app(obj, mk('br'))
        gdiv = mk('div')
        gdiv.setAttribute("id", "people_" + group)
        gdiv.style.border = "1px solid #999"
        gdiv.style.display = "none"
        for person in json.groups[group]
            pdiv = mk('div')
            set(pdiv, 'id', 'tag_' + group + '_' + person.id)
            app(pdiv, txt(person.name + " - <" + person.email + "> - "))
            a = mk('a')
            set(a, 'href', 'javascript:void(0);')
            set(a, 'onclick', "this.parentNode.parentNode.removeChild(this.parentNode); js = { untag: {} }; js.untag['" + person.id + "'] = '" + group + "'; postJSON('/api/2/affiliations', js, null, null, null);")
            app(a, txt("Remove from group"))
            app(pdiv, a)
            app(gdiv, pdiv)
        app(obj,gdiv)
    state.widget.inject(obj, true)

affiliationWizard = (json, state) ->
    obj = mk('div')
    groups = []
    for group, members of json.groups
        groups.push(group)
    groups.sort((a,b) => json.groups[b].length - json.groups[a].length)
    h3 = mk('h3')
    app(h3, txt("Found " + groups.length + " possible organisations/companies:"))
    app(obj, h3)
    p = mk('p')
    app(p, txt("Select a group or individuals within it to tag them as belonging to that group."))
    app(obj, p)
    for group in groups
        groupname = group.split(/\./)[0].replace(/^([a-z])/, (a) => a.toUpperCase())
        h4 = mk('h4')
        app(h4, txt(groupname + ": " + json.groups[group].length + " members"))
        h4.style.fontSize = "14pt"
        h4.setAttribute("onclick", "var a = get('people_" + group + "'); a.style.display = (a.style.display == 'block') ? 'none' : 'block';")
        id = Math.floor(Math.random() * 987654321).toString(16)
        chk = document.createElement('input')
        chk.setAttribute("type", "checkbox")
        chk.setAttribute("id", group)
        chk.style.marginLeft = '10px'
        chk.style.color = "#090"
        chk.style.fontSize = "16pt"
        chk.setAttribute("class", "f")
        chk.addEventListener("change", () ->
            group = this.getAttribute('id')
            for person in json.groups[group]
                chk = get('tag_' + person.id)
                chk.checked = this.checked
            )
        app(obj, chk)
        h4.style.display = "inline-block"
        h4.style.cursor = 'se-resize'
        app(obj, h4)
        app(obj, mk('br'))
        gdiv = mk('div')
        gdiv.setAttribute("id", "people_" + group)
        gdiv.style.border = "1px solid #999"
        gdiv.style.display = "none"
        for person in json.groups[group]
            chk = document.createElement('input')
            chk.setAttribute("type", "checkbox")
            chk.setAttribute("id", 'tag_' + person.id)
            chk.setAttribute("pid", person.id)
            chk.setAttribute("value", group)
            chk.style.marginLeft = '10px'
            chk.style.color = "#369"
            chk.style.fontSize = "10pt"
            label = document.createElement('label')
            label.setAttribute("for", 'tag_' + person.id)
            label.setAttribute("title", "Check this box to tag this person as affiliated with " + groupname)
            chk.setAttribute("title", "Check this box to tag this person as affiliated with " + groupname)
            label.style.paddingLeft = '5px'
            label.appendChild(document.createTextNode(person.name + " - <" + person.email + ">"))
            app(gdiv, chk)
            app(gdiv, label)
            a = mk('a')
            set(a, 'href', 'javascript:void(affiliate("' + person.id + '"));')
            app(a, txt("Set a tag"))
            app(gdiv, txt(" - "))
            app(gdiv, a)
            sp = mk('span')
            set(sp, 'id', 'tags_' + person.id)
            app(gdiv, sp)
            app(gdiv, mk('br'))
        app(obj,gdiv)
    
    btn = mk('input')
    set(btn, 'type', 'button')
    set(btn, 'class', 'btn btn-info')
    set(btn, 'value', 'Save changes')
    set(btn, 'widget', state.widget.id)
    btn.addEventListener("click", () ->
        w = findWidget(this.getAttribute('widget'))
        tagList = {}
        $( "[type=checkbox]" ).each( () ->
            pid = $(this).attr('pid')
            val = $(this).attr('value')
            if (pid and pid.length > 0 and ($(this).attr('checked') or $(this).is(':checked')))
                tagList[pid] = val
            )
        w.args.eargs = {
            tag: tagList
        }
        w.callback = affiliation
        w.reload()
    )
    app(obj, btn)
    state.widget.inject(obj, true)


affiliate = (hash) ->
    tag = window.prompt("Please enter the tag with which you wish to associate this source, or type nothing to untag.")
    if tag == ""
        tag = null
    tr = get('tags_' + hash)
    tags = {}
    tags[hash] = tag
    if tag
        postJSON('affiliations', { tag: tags }, null, null)
        app(tr, txt("(Tagged as: " + tag + ") "))
        
altemail = (hash) ->
    tag = window.prompt("Please enter the alt email with which you wish to associate this source, or type nothing to clear alts.")
    if tag == ""
        tag = null
    tr = get('tags_' + hash)
    tags = {}
    tags[hash] = tag
    if tag
        postJSON('affiliations', { altemail: tags }, null, null)
        app(tr, txt("(Affiliated as: " + tag + ") "))
        
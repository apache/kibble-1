orgadmin = (json, state) ->
    
    if globArgs.org and json.admin[globArgs.org]
        pdiv = document.createElement('div')
        id = globArgs.org
        title = json.admin[id]
        h2 = mk('h2')
        app(h2, txt("Editing: " + title))
        app(pdiv, h2)
        
        obj = mk('form')
        h4 = mk('h4')
        app(h4, txt("Invite a new user to this org:"))
        app(obj, h4)
        
        div = mk('div')
        app(div, txt("Username (email): "))
        inp = mk('input')
        set(inp, 'type', 'text')
        set(inp, 'name', 'who')
        inp.style.width = "200px"
        app(div, inp)
        app(obj, div)
        
        div = mk('div')
        app(div, txt("Make administrator: "))
        inp = mk('input')
        set(inp, 'type', 'checkbox')
        set(inp, 'name', 'admin')
        set(inp, 'value', 'true')
        app(div, inp)
        app(obj, div)
        
        btn = mk('input')
        set(btn, 'type', 'button')
        set(btn, 'onclick', 'addorguser(this.form)')
        set(btn, 'value', "Add user")
        app(obj, btn)
        
        app(pdiv, obj)
        
        
        obj = mk('form')
        h4 = mk('h4')
        app(h4, txt("Remove a user from the org:"))
        app(obj, h4)
        
        div = mk('div')
        app(div, txt("Username (email): "))
        inp = mk('input')
        set(inp, 'type', 'text')
        set(inp, 'name', 'who')
        inp.style.width = "200px"
        app(div, inp)
        app(obj, div)
        
        div = mk('div')
        app(div, txt("Just remove admin privs (if any): "))
        inp = mk('input')
        set(inp, 'type', 'checkbox')
        set(inp, 'name', 'admin')
        set(inp, 'value', 'true')
        app(div, inp)
        app(obj, div)
        
        btn = mk('input')
        set(btn, 'type', 'button')
        set(btn, 'onclick', 'remorguser(this.form)')
        set(btn, 'value', "Remove user")
        app(obj, btn)
        
        app(pdiv, obj)
        
        state.widget.inject(pdiv, true)
    else
        state.widget.inject(txt("You are not an admin of this organisation!"))

   

addorguser = (form) ->
    js = {
        action: 'add',
        org: globArgs.org
    }
    for i in [0..form.length-1]
        k = form[i].name
        v = form[i].value
        if k == 'who'
            form[i].value = ""
        if k == 'admin'
            v = if form[i].checked then 'true' else 'false'
        if k in ['who', 'admin']
            js[k] = v
    
    postJSON("admin-org", js, null, (a) -> alert("User added!") )

remorguser = (form) ->
    js = {
        action: 'remove',
        org: globArgs.org
    }
    for i in [0..form.length-1]
        k = form[i].name
        v = form[i].value
        if k == 'who'
            form[i].value = ""
        if k == 'admin'
            v = if form[i].checked then 'true' else 'false'
        if k in ['who', 'admin']
            js[k] = v
    
    postJSON("admin-org", js, null, (a) -> alert("User removed!") )
        
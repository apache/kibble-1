preferences = (json, state) ->
        obj = document.createElement('form')

        items =
            screenname: 'Screen name'
            fullname : "Full name"
            email : "Email address"
            tag : "Organisation filter tag"
            token: "API token"
        desc =
            tag: "If set, only sources with this tag will be shown in your views."
            
        for item in ['screenname', 'fullname', 'email', 'tag', 'token']
            div = mk('div')
            app(div, txt(items[item] + ": "))
            inp = mk('input')
            set(inp, 'type', 'text')
            set(inp, 'name', item)
            inp.style.width = "200px"
            if item == 'token'
                set(inp, "readonly", "readonly")
                set(inp, "disabled", "disabled")
                inp.style.width = "700px"
            set(inp, 'value', if json[item] then json[item] else '')
            app(div, inp)
            if desc[item]
                i = mk('i')
                i.style.fontSize = "9pt"
                i.style.marginLeft = "20px"
                app(i, txt(desc[item]))
                app(div, i)
            app(obj, div)
        div = mk('div')
        app(div, txt("Organisation to view: "))
        list = mk('select')
        set(list, 'name', 'organisation')
        for org in json.orgs
            opt = mk('option')
            opt.value = org
            opt.text = org
            if org == json.organisation
                opt.selected = 'selected'
            app(list, opt)
        app(div,list)
        app(obj, div)
        
        btn = mk('input')
        set(btn, 'type', 'button')
        set(btn, 'onclick', 'saveprefs(this.form)')
        set(btn, 'value', "Save preferences")
        app(obj, btn)
        
        #obj.innerHTML += JSON.stringify(json)
        state.widget.inject(obj, true)
        
        # Org admin?
        if json.admin
            aobj = mk('div')
            app(aobj, mk('br'))
            app(aobj, mk('br'))
            h1 = mk('h2')
            app(h1, txt("Organisation administration:"))
            app(aobj, h1)
            app(aobj, txt("If you are an organisation administrator, you may edit your organisation(s) by selecting the org you wish to edit below:"))
            for id, name of json.admin
                a = mk('a')
                set(a, 'href', '?page=orgadmin&org=' + id)
                h3 = mk('h4')
                app(h3, txt("- " + name))
                app(a, h3)
                app(aobj, a)
            state.widget.inject(aobj)

saveprefs = (form) ->
    js = {
        action: 'save'
    }
    for i in [0..form.length-1]
        k = form[i].name
        v = form[i].value
        if k in ['screenname', 'fullname', 'email', 'tag', 'organisation']
            js[k] = v
    postJSON("preferences", js, null, (a) -> alert("Preferences saved!") )
        
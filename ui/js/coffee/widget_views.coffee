newview = []

saveview = (id) ->
    if not id
        if get('viewname').value == ''
            alert('Please enter a name for this view!')
            return
        newview = []
        $( "[datatype=source]" ).each( () ->
                pid = $(this).attr('id')
                sel = $(this).attr('selected')||"blorp"
                if sel == "selected"
                    newview.push(pid)
            )
        viewname = get('viewname').value
        publicView = false
        if get('public')
            publicView = get('public').checked
        view = {
            id: 'makeone',
            name: viewname,
            sources: newview,
            public: publicView
        }
        put('views', view, null, () ->
            window.setTimeout(() ->
                location.href = '?page=views'
            , 1500)
            )
    else
        view = {
            id: id,
            sources: newview
        }
        patch('views', view, null, () ->
            window.setTimeout(() ->
                location.href = '?page=views'
            , 1500)
            )

rmview = (id) ->
    xdelete('views', { id: id }, null, () ->
            window.setTimeout(() ->
                location.href = '?page=views'
            , 1500)
            )

newview = []
currentSources = {}

filterView = (val) ->
    re = new RegExp(val, 'i')
    newview = []
    for source, url of currentSources
        me = get(source)
        me.removeAttribute('selected')
        me.style.background = "none"
        me.style.color = "#000"
        if val.length > 0
            me.style.display = 'none'
        else
            me.style.display = 'block'
        if val.length > 0 and url.match(re)
            me.setAttribute("selected", "true")
            me.style.background = "#4B8"
            me.style.color = "#FFF"
            me.style.display = 'block'
            
manageviews = (json, state) ->
    
    obj = mk('div')
    p = mk('p')
    app(p, txt("Views allow you to quickly set up a group of sources to view as a sub-organisation, much like tags, but faster."))
    app(obj, p)
    h3 = mk('h3')
    noviews = json.views.length || 0
    app(h3, txt("You currently have " + noviews + " view" + (if noviews == 1 then '' else 's') + " in your database "))
    
    btn = mk('input')
    set(btn, 'type', 'button')
    set(btn, 'class', 'btn btn-success')
    set(btn, 'value', 'Create a new view')
    set(btn, 'onclick', 'get("newdiv").style.display = "block"; this.style.display = "none";')
    app(h3, btn)    
    app(obj, h3)
    
    newdiv = mk('div')
    set(newdiv, 'id', 'newdiv')
    newdiv.style.display = "none"
    json.sources.sort((a,b) -> return ( if a.type == b.type then  (if a.sourceURL > b.sourceURL then 1 else -1)  else (if (b.type < a.type) then 1 else -1) ))
    inp = mk('input')
    set(inp, 'type', 'text')
    set(inp, 'id', 'viewname')
    app(newdiv, txt("Name your new view: "))
    app(newdiv, inp)
    app(newdiv, mk('br'))
    
    if userAccount.userlevel == 'admin' or userAccount.defaultOrganisation in userAccount.ownerships
        inp = mk('input')
        set(inp, 'type', 'checkbox')
        set(inp, 'id', 'public')
        app(newdiv, txt("Make view public (global): "))
        app(newdiv, inp)
        app(newdiv, mk('br'))
    
    inp = mk('input')
    set(inp, 'type', 'text')
    set(inp, 'id', 'viewfilter')
    set(inp, 'oninput', "filterView(this.value)")
    app(newdiv, txt("Filter-select: "))
    app(newdiv, inp)
    app(newdiv, mk('i', {}, "You can use the filter-select to quickly mark sources based on a regex. Type in 'foo' to select all sources matching 'foo' etc."))
    app(newdiv, mk('br'))
    
    app(newdiv, txt("Select the sources you wish to add to this view below:"))
    app(newdiv, mk('br'))
    btn = mk('input')
    set(btn, 'type', 'button')
    set(btn, 'class', 'btn btn-danger')
    set(btn, 'value', 'Save view')
    set(btn, 'onclick', 'saveview();')
    app(newdiv, btn)
    for source in json.sources
        currentSources[source.sourceID] = source.sourceURL
        sdiv = mk('div')
        set(sdiv, 'id', source.sourceID)
        set(sdiv, 'datatype', 'source')
        sdiv.style.cursor = 'pointer'
        sdiv.style.margin = "3px"
        sdiv.style.border = "1px solid #666"
        sdiv.style.color = "#000"
        sdiv.addEventListener("click", () ->
            w = findWidget(this.getAttribute('widget'))
            selected = this.getAttribute("selected")
            if selected and selected == "true"
                this.style.background = "none"
                this.style.color = "#000"
                set(this, 'selected', 'false')
            else
                this.style.background = "#4B8"
                this.style.color = "#FFF"
                set(this, 'selected', 'true')
            newview = []
        )
        app(sdiv, txt(source.sourceURL))
        app(newdiv, sdiv)
    btn = mk('input')
    set(btn, 'type', 'button')
    set(btn, 'class', 'btn btn-danger')
    set(btn, 'value', 'Save view')
    set(btn, 'onclick', 'saveview();')
    app(newdiv, btn)
        
    app(obj, newdiv)
    for view in json.views
        popdiv = mk('div')
        popdiv.style.paddingLeft = "10px"
        popdiv.style.margin = "3px"
        popdiv.style.borderRadius = "4px"
        h4 = mk('h4')
        app(h4, txt(view.name + " - " + view.sourceList.length + " sources"))
        popdiv.style.border = "1px solid #333"
        popdiv.style.background = "#323234"
        h4.style.display = "inline-block"
        app(popdiv, h4)
        
        
        btn = mk('input')
        set(btn, 'type', 'button')
        set(btn, 'class', 'btn btn-warning')
        set(btn, 'value', 'Edit view')
        set(btn, 'onclick', "get('" + view.id + "').style.display = (get('" + view.id + "').style.display == 'block') ? 'none' : 'block'")
        btn.style.marginLeft = "20px"
        btn.style.padding = "2px"
        app(popdiv, btn)

        btn = mk('input')
        set(btn, 'type', 'button')
        set(btn, 'class', 'btn btn-danger')
        set(btn, 'value', 'Delete view')
        set(btn, 'onclick', 'rmview("' + view.id + '");')
        btn.style.marginLeft = "20px"
        btn.style.padding = "2px"
        app(popdiv, btn)
        
        btn = mk('input')
        set(btn, 'type', 'button')
        set(btn, 'class', 'btn btn-success')
        set(btn, 'value', 'Save changes')
        set(btn, 'onclick', 'saveview("' + view.id + '");')
        btn.style.marginLeft = "20px"
        btn.style.padding = "2px"
        app(popdiv, btn)
        
        h4.style.color = "#FFA"
        h4.style.cursor = 'pointer'
        set(h4, 'onclick', "get('" + view.id + "').style.display = (get('" + view.id + "').style.display == 'block') ? 'none' : 'block'")
        newdiv = mk('div')
        set(newdiv, 'id', view.id)
        newdiv.style.display = "none"
        inp = mk('input')
        set(inp, 'type', 'text')
        set(inp, 'id', 'viewname')
        app(newdiv, txt("Select the sources you wish to have in this view below:"))
        for source in json.sources
            sdiv = mk('div')
            set(sdiv, 'id', view.id + "_" + source.sourceID)
            set(sdiv, 'datatype', view.id)
            sdiv.style.cursor = 'pointer'
            sdiv.style.margin = "3px"
            sdiv.style.border = "1px solid #666"
            sdiv.style.color = "#000"
            if source.sourceID in view.sourceList
                sdiv.style.background = "#4B8"
                sdiv.style.color = "#FFF"
                set(sdiv, 'selected', 'selected')
            else
                set(sdiv, 'selected', 'false')
            sdiv.addEventListener("click", () ->
                selected = this.getAttribute("selected")
                vid = this.getAttribute("datatype")
                if selected and selected == "selected"
                    this.style.background = "none"
                    this.style.color = "#000"
                    set(this, 'selected', 'false')
                else
                    this.style.background = "#4B8"
                    this.style.color = "#FFF"
                    set(this, 'selected', 'selected')
                newview = []
                $( "[datatype="+vid+"]" ).each( () ->
                    pid = $(this).attr('id').split(/_/)[1]
                    sel = this.getAttribute("selected")
                    if sel == 'selected'
                        newview.push(pid)
                )
            )
            app(sdiv, txt(source.sourceURL))
            app(newdiv, sdiv)
        btn = mk('input')
        set(btn, 'type', 'button')
        set(btn, 'class', 'btn btn-success')
        set(btn, 'value', 'Save view')
        set(btn, 'onclick', 'saveview("' + view.id + '");')
        app(newdiv, btn)
        app(obj, popdiv)
        app(obj, newdiv)
    state.widget.inject(obj, true)    
        
        
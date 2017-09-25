mvp = (json, state) ->
    nlist = new HTML('select', { name: 'size', id: 'size'})
    for i in [10,20,50,100,200,500,1000,2000]
        el = new HTML('option', { value: i, text: i+""})
        if globArgs.size and parseInt(globArgs.size) == i
            el.selected = 'selected'
        el.inject(txt(i+""))
        nlist.inject(el)
    nlist.addEventListener("change", () ->
            n = this.value
            if n == ""
                    n = null
            globArgs.size = n
            updateWidgets('mvp', null, { size: n })
                
        , false)
    state.widget.inject(
        new HTML('b', {}, "List size: "),
        true
    )
    state.widget.inject(nlist)
    
    
    nlist = new HTML('select', { name: 'sort', id: 'sort'})
    for i in ['commits', 'issues', 'emails']
        el = new HTML('option', { value: i, text: i})
        if globArgs.sort and globArgs.sort == i
            el.selected = 'selected'
        el.inject(txt(i))
        nlist.inject(el)
    nlist.addEventListener("change", () ->
            n = this.value
            if n == ""
                    n = null
            globArgs.sort = n
            updateWidgets('mvp', null, { sort: n })
                
        , false)
    state.widget.inject(
        new HTML('b', {}, " Sort by: "),
    )
    state.widget.inject(nlist)
    
    tbl = mk('table', {class: "table table-striped"})
    tr = mk('tr', {}, [
        mk('th', {}, "Rank"),
        mk('th', {}, "Avatar"),
        mk('th', {}, "Name",)
        mk('th', {}, "Address"),
        mk('th', {}, if globArgs.author then "Authorings" else "Commits"),
        mk('th', {}, "Issues"),
        mk('th', {}, "Email")
        ])
    app(tbl, tr)
    tb = new HTML('tbody')
    for person, i in json.sorted
        tr = mk('tr', {scope: 'row'}, [
            mk('td', {}, (i+1).pretty()),
            mk('td', {}, new HTML('img', {style: { width: '32px', height: '32px'}, class: "img-circle img-responsive", src:"https://secure.gravatar.com/avatar/#{person.md5}.png?d=identicon"})),
            mk('td', {}, mk('a', { href: "?page=people&email=#{person.address}"}, person.name)),
            mk('td', {}, person.address),
            mk('td', {}, person.commits.pretty()),
            mk('td', {}, person.issues.pretty()),
            mk('td', {}, person.emails.pretty()),
            ])
        tb.inject(tr)
    app(tbl, tb)
    state.widget.inject(tbl)
    #updateWidgets('trends', null, { email: email })

              
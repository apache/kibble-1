comstat = (json, state) ->
    
    if json and json.stats
        row = new Row()
        p = new HTML('p', {},
                     if (globArgs.committersOnly == 'true') then \
                        "You are currently only seeing stats for committers. To view statistics for all contributors (committers and authors), please uncheck the box below:" else \
                        "You are currently seeing stats for both committership and authorship of code. To view only committership stats, tick the box below:"
                     )
        chk = new HTML('input', {
            type: 'checkbox',
            checked: if globArgs.committersOnly == 'true' then 'checked' else null,
            id: 'comonly',
            onchange: 'updateWidgets("comstat", null, { committersOnly: this.checked ? "true" : null });'
            })
        lb = new HTML('label', { for: 'comonly' }, "Show only new committers, discard new authors.")
        
        row.inject(p)
        row.inject(chk)
        row.inject(lb)
        state.widget.inject(row.div, true)
        
        if json.stats.code.seen > 0
            row = new Row()
            js = { alphaSort: true, counts: {
                "Regulars": json.stats.code.seen - json.stats.code.newcomers - json.stats.code.returning,
                "Newcomers": json.stats.code.newcomers,
                "Returning": json.stats.code.returning
                }
            }
            widget = new Widget(4, {name: "Code contributors this period", representation: 'comstat'})
            widget.json = js
            widget.callback = donut
            widget.parent = state.widget
            row.inject(widget)
            donut(js, { widget: widget})
            nl = 0
            if json.stats.code.newtbl.length and json.stats.code.newtbl.length >= 0
                nl = json.stats.code.newtbl.length
            stbl = new Widget(4, { name: "New code contributors (#{nl})" })
            
            tbl = mk('table', {class: "table table-striped"})
            tr = mk('tr', {}, [
                mk('th', {}, "Avatar"),
                mk('th', {}, "Name",)
                mk('th', {}, "Address"),
                ])
            app(tbl, tr)
            tb = new HTML('tbody')
            for person, i in json.stats.code.newtbl
                if i > 6
                    m = json.stats.code.newtbl.length - 7
                    tr = mk('tr', {scope: 'row'}, [
                        mk('td', {colspan: "3"}, "+#{m} more...")
                        ])
                    tb.inject(tr)
                    break
                tr = mk('tr', {scope: 'row'}, [
                    mk('td', {}, new HTML('img', {style: { width: '32px', height: '32px'}, class: "img-circle img-responsive", src:"https://secure.gravatar.com/avatar/#{person.md5}.png?d=identicon"})),
                    mk('td', {}, mk('a', { href: "?page=people&email=#{person.address}"}, person.name)),
                    mk('td', {}, person.address),
                    ])
                tb.inject(tr)
            app(tbl, tb)
            stbl.inject(tbl)
            row.inject(stbl)
            
            if json.stats.code.timeseries and json.stats.code.timeseries.length > 0
                widget = new Widget(4, {name: "New code contributors over time:", representation: 'bars'})
                widget.parent = state.widget
                row.inject(widget)
                js = {widgetType: { chartType: 'bar'}, timeseries: json.stats.code.timeseries}
                widget.json = js
                widget.callback = linechart
                linechart(js, { widget: widget})
            
            state.widget.inject(row.div)
            
        if json.stats.issues.seen > 0
            row = new Row()
            js = { alphaSort: true, counts: {
                "Regulars": json.stats.issues.seen - json.stats.issues.newcomers - json.stats.issues.returning,
                "Newcomers": json.stats.issues.newcomers,
                "Returning": json.stats.issues.returning
                }
            }
            widget = new Widget(4, {name: "Issue contributors this period", representation: 'comstat'})
            widget.json = js
            widget.parent = state.widget
            widget.callback = donut
            row.inject(widget)
            donut(js, { widget: widget})
            nl = 0
            if json.stats.issues.newtbl.length and json.stats.issues.newtbl.length >= 0
                nl = json.stats.issues.newtbl.length
            stbl = new Widget(4, { name: "New issue contributors (#{nl})" })
            
            tbl = mk('table', {class: "table table-striped"})
            tr = mk('tr', {}, [
                mk('th', {}, "Avatar"),
                mk('th', {}, "Name",)
                mk('th', {}, "Address"),
                ])
            app(tbl, tr)
            tb = new HTML('tbody')
            for person, i in json.stats.issues.newtbl
                if i > 6
                    m = json.stats.issues.newtbl.length - 7
                    tr = mk('tr', {scope: 'row'}, [
                        mk('td', {colspan: "3"}, "+#{m} more...")
                        ])
                    tb.inject(tr)
                    break
                tr = mk('tr', {scope: 'row'}, [
                    mk('td', {}, new HTML('img', {style: { width: '32px', height: '32px'}, class: "img-circle img-responsive", src:"https://secure.gravatar.com/avatar/#{person.md5}.png?d=identicon"})),
                    mk('td', {}, mk('a', { href: "?page=people&email=#{person.address}"}, person.name)),
                    mk('td', {}, person.address),
                    ])
                tb.inject(tr)
            app(tbl, tb)
            stbl.inject(tbl)
            row.inject(stbl)
            
            if json.stats.issues.timeseries and json.stats.issues.timeseries.length > 0
                widget = new Widget(4, {name: "New issue contributors over time:", representation: 'bars'})
                widget.parent = state.widget
                row.inject(widget)
                js = {widgetType: { chartType: 'bar'}, timeseries: json.stats.issues.timeseries}
                widget.json = js
                widget.callback = linechart
                linechart(js, { widget: widget})
            
            
            state.widget.inject(row.div)
            
        if json.stats.converts.issue_to_code.length and json.stats.converts.issue_to_code.length > 0
            row = new Row()
            
            stbl = new Widget(6, { name: "Previous issue contributors who are now contributing code:" })
            
            tbl = mk('table', {class: "table table-striped"})
            tr = mk('tr', {}, [
                mk('th', {}, "Avatar"),
                mk('th', {}, "Name",)
                mk('th', {}, "Address"),
                mk('th', {}, "Days from first issue to first code contribution:"),
                ])
            app(tbl, tr)
            tb = new HTML('tbody')
            for person, i in json.stats.converts.issue_to_code
                if i > 20
                    break
                tr = mk('tr', {scope: 'row'}, [
                    mk('td', {}, new HTML('img', {style: { width: '32px', height: '32px'}, class: "img-circle img-responsive", src:"https://secure.gravatar.com/avatar/#{person.md5}.png?d=identicon"})),
                    mk('td', {}, mk('a', { href: "?page=people&email=#{person.address}"}, person.name)),
                    mk('td', {}, person.address),
                    mk('td', {style: { textAlign: 'right'}}, (Math.floor(person.tdiff / (86400))).pretty()),
                    ])
                tb.inject(tr)
            app(tbl, tb)
            stbl.inject(tbl)
            row.inject(stbl)
            
            state.widget.inject(row.div)
        
        if json.stats.converts.email_to_code.length and json.stats.converts.email_to_code.length > 0
            row = new Row()
            
            stbl = new Widget(6, { name: "Previous email authors who are now contributing code:" })
            
            tbl = mk('table', {class: "table table-striped"})
            tr = mk('tr', {}, [
                mk('th', {}, "Avatar"),
                mk('th', {}, "Name",)
                mk('th', {}, "Address"),
                mk('th', {}, "Days from first email to first code contribution:"),
                ])
            app(tbl, tr)
            tb = new HTML('tbody')
            for person, i in json.stats.converts.email_to_code
                if i > 20
                    break
                tr = mk('tr', {scope: 'row'}, [
                    mk('td', {}, new HTML('img', {style: { width: '32px', height: '32px'}, class: "img-circle img-responsive", src:"https://secure.gravatar.com/avatar/#{person.md5}.png?d=identicon"})),
                    mk('td', {}, mk('a', { href: "?page=people&email=#{person.address}"}, person.name)),
                    mk('td', {}, person.address),
                    mk('td', {style: { textAlign: 'right'}}, (Math.floor(person.tdiff / (86400))).pretty()),
                    ])
                tb.inject(tr)
            app(tbl, tb)
            stbl.inject(tbl)
            row.inject(stbl)
            
            state.widget.inject(row.div)
    else
        notice = new HTML('h2', {}, "Community growth stats only works with user-defined views!")
        p = new HTML('p', {}, "To see community growth stats, please create a view of the code, email, bugs you wish to view stats for, or select an existng view in the list above")
        state.widget.inject(notice, true)
        state.widget.inject(p)
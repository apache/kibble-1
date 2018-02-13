comShow = (t) ->
    rows = document.getElementsByTagName("tr")
    for row in rows
        if (row.getAttribute("id")||"foo").match("comstat_#{t}_")
            row.style.display = "table-row"
    document.getElementById("comstat_#{t}_more").style.display = "none"
    
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
                "Regulars": json.stats.code.seen - json.stats.code.newcomers.length,
                "Newcomers": json.stats.code.newcomers.length,
                }
            }
            widget = new Widget(4, {name: "Code contributors this period", representation: 'comstat'})
            widget.json = js
            widget.callback = donut
            widget.parent = state.widget
            row.inject(widget)
            donut(js, { widget: widget})
            nl = 0
            if json.stats.code.newcomers.length and json.stats.code.newcomers.length >= 0
                nl = json.stats.code.newcomers.length
            stbl = new Widget(6, { name: "New code contributors (#{nl})" })
            
            tbl = mk('table', {class: "table table-striped"})
            tr = mk('tr', {}, [
                mk('th', {}, "Avatar"),
                mk('th', {}, "Name",)
                mk('th', {}, "Address"),
                mk('th', {}, "First commit"),
                ])
            app(tbl, tr)
            tb = new HTML('tbody')
            json.stats.code.newcomers.sort((a,b) => json.bios[b].code[0] - json.bios[a].code[0])
            dstyle = 'table-row'
            for person, i in json.stats.code.newcomers
                oemail = person
                hash = json.bios[person].code[1].id.split('/')[1]
                repo = json.bios[person].code[1].sourceURL
                wh = new Date(json.bios[person].code[0] * 1000.0).toDateString()
                person = json.bios[person].bio
                if i == 6
                    m = json.stats.code.newcomers.length - i
                    tr = mk('tr', {scope: 'row', id: 'comstat_code_more'}, [
                        mk('td', {colspan: "3"}, new HTML('a', { href: 'javascript:void(comShow("code"));'}, "+#{m} more..."))
                        ])
                    tb.inject(tr)
                    dstyle = "none"

                tr = new HTML('tr', {scope: 'row', id: "comstat_code_#{i}", style: { display: dstyle}}, [
                    mk('td', {}, new HTML('img', {style: { width: '32px', height: '32px'}, class: "img-circle img-responsive", src:"https://secure.gravatar.com/avatar/#{person.md5}.png?d=identicon"})),
                    mk('td', {}, mk('a', { href: "?page=people&email=#{oemail}"}, person.name)),
                    mk('td', {}, oemail),
                    mk('td', {}, "#{wh} (#{repo})"),
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
                "Regulars": json.stats.issues.seen - json.stats.issues.newcomers.length,
                "Newcomers": json.stats.issues.newcomers.length
                }
            }
            widget = new Widget(4, {name: "Issue contributors this period", representation: 'comstat'})
            widget.json = js
            widget.parent = state.widget
            widget.callback = donut
            row.inject(widget)
            donut(js, { widget: widget})
            nl = 0
            if json.stats.issues.newcomers.length and json.stats.issues.newcomers.length >= 0
                nl = json.stats.issues.newcomers.length
            stbl = new Widget(6, { name: "New issue contributors (#{nl})" })
            
            tbl = mk('table', {class: "table table-striped"})
            tr = mk('tr', {}, [
                mk('th', {}, "Avatar"),
                mk('th', {}, "Name",)
                mk('th', {}, "Address"),
                mk('th', {}, "First issue"),
                ])
            app(tbl, tr)
            tb = new HTML('tbody')
            json.stats.issues.newcomers.sort((a,b) => json.bios[b].issue[0] - json.bios[a].issue[0])
            dstyle = 'show'
            for person, i in json.stats.issues.newcomers
                oemail = person
                url = json.bios[person].issue[1].url
                key = json.bios[person].issue[1].key || url
                wh = new Date(json.bios[person].issue[0] * 1000.0).toDateString()
                person = json.bios[person].bio
                
                if i == 6
                    m = json.stats.issues.newcomers.length - i
                    tr = mk('tr', {scope: 'row', id: 'comstat_issue_more'}, [
                        mk('td', {colspan: "3"}, new HTML('a', { href: 'javascript:void(comShow("issue"));'}, "+#{m} more..."))
                        ])
                    tb.inject(tr)
                    dstyle = "none"

                tr = new HTML('tr', {scope: 'row', id: "comstat_issue_#{i}", style: { display: dstyle}}, [
                    mk('td', {}, new HTML('img', {style: { width: '32px', height: '32px'}, class: "img-circle img-responsive", src:"https://secure.gravatar.com/avatar/#{person.md5}.png?d=identicon"})),
                    mk('td', {}, mk('a', { href: "?page=people&email=#{oemail}"}, person.name)),
                    mk('td', {}, oemail),
                    mk('td', {}, ["#{wh} (", mk('a', { href: url||"#"}, txt(key)), ")"]),
                    ])
                tb.inject(tr)
            app(tbl, tb)
            stbl.inject(tbl)
            row.inject(stbl)
            
            if json.stats.issues.timeseries and json.stats.issues.timeseries.length > 0
                widget = new Widget(6, {name: "New issue contributors over time:", representation: 'bars'})
                widget.parent = state.widget
                row.inject(widget)
                js = {widgetType: { chartType: 'bar'}, timeseries: json.stats.issues.timeseries}
                widget.json = js
                widget.callback = linechart
                linechart(js, { widget: widget})
            
            
            state.widget.inject(row.div)
        if json.stats.converts
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
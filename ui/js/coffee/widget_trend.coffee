
trendBox = (icon, count, title, desc) ->
        icons = {
                comment: 'fa-comments-o',
                down: 'fa-sort-amount-desc',
                up: 'fa-sort-amount-asc',
                check: 'fa-check-square-o',
                caret: 'fa-caret-square-o-right',
                spin: 'fa-spin fa-cog'
        }
        div = document.createElement('div')
        div.setAttribute("class", "animated flipInY col-lg-3 col-md-3 col-sm-6 col-xs-12")
        cdiv = document.createElement('div')
        cdiv.setAttribute("class", "tile-stats")
        cdiv.style.width = "100%"
        idiv = document.createElement('div')
        idiv.setAttribute("class", "icon")
        i = document.createElement('i')
        i.setAttribute("class", "fa " + (icons[icon] || 'fa-comments-o'))
        idiv.appendChild(i)
        cdiv.appendChild(idiv)
        
        # Count
        codiv = document.createElement('div')
        codiv.setAttribute("class", "count")
        codiv.appendChild(document.createTextNode(count))
        cdiv.appendChild(codiv)
        
        # Title
        h3 = document.createElement('h4')
        h3.appendChild(document.createTextNode(title))
        cdiv.appendChild(h3)
        
        # Description
        p = document.createElement('p')
        p.appendChild(document.createTextNode(desc))
        cdiv.appendChild(p)
        
        div.appendChild(cdiv)
        return div

trend = (json, state) ->
        console.log(state.widget.args.source)
        if json.trends # api 2 version
            wipe = true
            for key, data of json.trends
                # Lines changed
                linediff = ""
                icon = 'up'
                if data.before > 0 and data.after > 0
                    diff = (data.after - data.before) / (data.before || 1)
                    if diff >= 0
                        linediff = "Up " + Math.floor(diff*100) + "% since last period"
                    else
                        linediff = "Down " + Math.floor(diff*100) + "% since last period"
                        icon = 'check'
                tb = trendBox(icon, data.after.pretty(), data.title, linediff)
                state.widget.inject(tb, wipe)
                wipe = false
                
        
            
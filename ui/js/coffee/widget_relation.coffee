relationship = (json, state) ->
        div = document.createElement('div')
        state.widget.inject(div, true)
        chart = new Chart(div, 'relationship', json, {})
        
        
        id = Math.floor(Math.random() * 987654321).toString(16)
        invchk = new HTML('input', { class: "uniform", style: { marginRight: "10px"}, id: "author_#{id}", type: 'checkbox', checked: globArgs.author, name: 'author', value: 'true' })
        
        invchk.addEventListener("change", () ->
                author = null
                if this.checked
                        author = 'true'
                        globArgs['author'] = 'true'
                
                updateWidgets('relationship', null, { author: author })
                )
        invlbl = new HTML('label', { for: "author_#{id}"}, "Inverse map (sender <-> recipient)")
        state.widget.inject(invchk)
        state.widget.inject(invlbl)
        
        state.widget.inject(new HTML('br'))
        state.widget.inject(new HTML('span', {}, "Minimum signal strength: "))
        sigsel = new HTML('select', {id: "signal_#{id}"})
        for i in [1..5]
                opt = new HTML('option', { value: i, selected:  if (String(i) == globArgs.links) then "selected" else null}, String(i))
                sigsel.inject(opt)
        sigsel.addEventListener("change", () ->
                links = null
                if this.value
                        links = this.value
                        globArgs['links'] = links
                
                updateWidgets('relationship', null, { links: links })
                )
        state.widget.inject(sigsel)
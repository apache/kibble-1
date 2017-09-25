# Donut widget

radarIndicators = []

radar = (json, state) ->
        
    lmain = new HTML('div')
    state.widget.inject(lmain, true)
    
    radarChart = new Chart(lmain, 'radar', json.radar)
    
    
    # Harmonizer
    id = Math.floor(Math.random() * 987654321).toString(16)
    chk = document.createElement('input')
    chk.setAttribute("type", "checkbox")
    chk.setAttribute("id", id)
    chk.style.marginLeft = '10px'
    if globArgs.harmonize and globArgs.harmonize == 'true'
            chk.checked = true
    chk.addEventListener("change", () ->
            harmonize = null
            if this.checked
                    harmonize = 'true'
                    globArgs['harmonize'] = 'true'
            
            updateWidgets('radar', null, { harmonize: harmonize })
            )
    state.widget.inject(mk('br'))
    state.widget.inject(chk)
    label = document.createElement('label')
    label.setAttribute("for", id)
    label.setAttribute("title", "Check this box to harmonize edges to organisational averages")
    chk.setAttribute("title", "Check this box to harmonize edges to organisational averages")
    label.style.paddingLeft = '5px'
    label.appendChild(document.createTextNode('Harmonize edges'))
    state.widget.inject(label)
    
    # Relativizer
    id = Math.floor(Math.random() * 987654321).toString(16)
    chk = document.createElement('input')
    chk.setAttribute("type", "checkbox")
    chk.setAttribute("id", id)
    chk.style.marginLeft = '10px'
    if globArgs.relativize and globArgs.relativize == 'true'
            chk.checked = true
    chk.addEventListener("change", () ->
            relativize = null
            if this.checked
                    relativize = 'true'
                    globArgs['relativize'] = 'true'
            
            updateWidgets('radar', null, { relativize: relativize })
            )
    state.widget.inject(mk('br'))
    state.widget.inject(chk)
    label = document.createElement('label')
    label.setAttribute("for", id)
    label.setAttribute("title", "Check this box to force all areas to be relative to their own projects (and not the compared projects). This may help to display foucs areas.")
    chk.setAttribute("title", "Check this box to force all areas to be relative to their own projects (and not the compared projects). This may help to display foucs areas.")
    label.style.paddingLeft = '5px'
    label.appendChild(document.createTextNode('Make all projects relative to themselves'))
    state.widget.inject(label)
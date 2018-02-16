# Donut widget
donut = (json, state) ->
        
    dt = []
    dtl = []
    l = 0
    tot = 0
    ttot = 0
    top = []
    if json.counts
        dtl = []
        dt = []
        a = 0
        for item, count of json.counts
            dt.push({name: item, value: count})
            a++
        if not json.alphaSort
            dt.sort((a,b) => b.value - a.value)
        else
            dt.sort((a,b) => if a.name > b.name then 1 else -1)
        for item in dt
            dtl.push(dt.name)
        theme.color = genColors(a+1, 0.55, 0.475, true) #quickColors(a)
        
    if (state.widget.args.representation == 'commentcount')
        code = 0
        comment = 0
        blank = 0
        langs = json.languages
        for lang, data of langs
                code += data.code
                comment += data.comment
                blank += data.blank||0
        
        tot = code + comment
        dtl = ['Code', 'Comments']
        dt = [
                {name: 'Code', value: code},
                {name: 'Comments', value: comment}
        ]
        if blank > 0
                dt.push({name: "Blanks", value: blank})
                
        theme.color = genColors(3, 0.6, 0.5, true)
    
    
    if (state.widget.args.representation == 'sloccount' or (state.widget.args.representation != 'commentcount' and json.languages))
        langs = json.languages
        for lang, data of langs
            tot += data.code
            top.push(lang)
        
        top.sort((a,b) => langs[b].code - langs[a].code)
        for lang in top
            l++
            if (l > 250 || (langs[lang].code/tot) < 0.01)
                break
            ttot += langs[lang].code
            dt.push( {
                    name: lang,
                    value: langs[lang].code
            })
            dtl.push(lang)
            
        if (tot != ttot) 
            dtl.push('Other languages')
            dt.push( {
                name: 'Other languages',
                value: (tot-ttot)
                })
        
        theme.color = genColors(17, 0.6, 0.5, true)
    
    data = {}
    for el in dt
        data[el.name] = el.value
    div = new HTML('div')
    state.widget.inject(div, true)
    chartBox = new Chart(div, 'donut', data, 25)
    
      
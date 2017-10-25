# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

chartWrapperButtons = {
    generic: [
        {
            id: 'download',
            icon: 'fa fa-download',
            title: "Export Image",
            onclick: (o) -> chartToSvg(o)
        },
        {
            id: 'svg',
            icon: 'fa fa-archive',
            title: "Export as SVG",
            onclick: (o) -> chartToSvg(o, true)
        },{
            id: 'dataview',
            icon: 'fa fa-book',
            title: "Data View",
            onclick: (o) -> dataTable(o)
        },
        {
            id: 'fullscreen',
            icon: 'fa fa-plus-square',
            title: "Switch to fullscreen",
            onclick: (o) -> fScreen(o)
        }
    ],
    line: [
        {
            icon: 'fa fa-bar-chart',
            title: "Show as Bar Chart",
            onclick: (o) -> switchChartType(o, o.config, 'bar')
        },
        {
            icon: 'fa fa-line-chart',
            title: "Show as Line Chart",
            onclick: (o) -> switchChartType(o, o.config, 'line')
        },{
            icon: 'fa fa-area-chart',
            title: "Show as Area Chart",
            onclick: (o) -> switchChartType(o, o.config, 'area-spline')
        },{
            icon: 'fa fa-bars',
            title: "Stack values",
            onclick: (o) -> stackChart(o, o.config, o.chartobj)
        },
        {
            icon: 'fa fa-object-ungroup',
            title: "Show sub-chart",
            onclick: (o) -> o.config.subchart = { show: if o.config.subchart and o.config.subchart.show then false else true}; o.chartobj = c3.generate(o.config);
        }
    ]
}

xxCharts = {}


fScreen = (o) ->
    xclass = o.main.getAttribute('class')
    if not xclass.match('chartModal')
        o.main.className = "chartModal chartWrapper"
        o.main.style.minHeight = "100% !important"
        o.buttons['fullscreen'].childNodes[0].className = 'fa fa-minus-square'
        o.buttons['fullscreen'].title = "Restore window"
        o.main.childNodes[2].style.minHeight = (window.innerHeight - 60) + "px"
        if o.config.donut
            o.config.donut.width = 120
            switchChartType(o, o.config, 'donut')
        if o.config.linked
          bb = o.main.childNodes[2].getBoundingClientRect()
          o.chartobj.resize({height: bb.height})
        else
          o.chartobj.resize({height: 720})
    else
        o.main.className = "chartWrapper"
        o.main.childNodes[2].style.minHeight = ""
        o.buttons['fullscreen'].title = "Switch to fullscreen"
        o.buttons['fullscreen'].childNodes[0].className = 'fa fa-plus-square'
        if o.config.donut
            o.config.donut.width = 50
            switchChartType(o, o.config, 'donut')
        if o.config.linked
          bb = o.main.childNodes[2].getBoundingClientRect()
          o.chartobj.resize({height: bb.height})
        else
          o.chartobj.resize({height: 240})
    return true


copyCSS = (destination, source) ->
   containerElements = ["svg","g"]
   if destination.childNodes.length > 0
        for cd in [0..destination.childNodes.length-1]
            child = destination.childNodes[cd]

            if (child.tagName in containerElements)
                 copyCSS(child, source.childNodes[cd])
                 continue
            
            style = source.childNodes[cd].currentStyle || window.getComputedStyle(source.childNodes[cd]);
            if (style == "undefined" || style == null)
             continue
            for st in style
                 child.style.setProperty(st, style.getPropertyValue(st))

downloadBlob = (name, uri) ->
    if (navigator.msSaveOrOpenBlob)
      navigator.msSaveOrOpenBlob(uriToBlob(uri), name);
    else
      saveLink = document.createElement('a');
    
      saveLink.download = name;
      saveLink.style.display = 'none';
      document.body.appendChild(saveLink);
      try
        blob = uriToBlob(uri);
        url = URL.createObjectURL(blob);
        saveLink.href = url;
        saveLink.onclick = () ->
          requestAnimationFrame( () ->
            URL.revokeObjectURL(url)
          )
        
      catch e
        console.warn('This browser does not support object URLs. Falling back to string URL.');
        saveLink.href = uri;
      
      saveLink.click()
      document.body.removeChild(saveLink)
     
    
chartToSvg = (o, asSVG) ->
    
    doctype = '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'
    svgdiv = o.chartdiv.getElementsByTagName('svg')[0]
    svgcopy = svgdiv.cloneNode(true)
    copyCSS(svgcopy, svgdiv)
    rect = o.main.getBoundingClientRect()
    svgcopy.setAttribute('xlink', 'http://www.w3.org/1999/xlink')
    
    source = (new XMLSerializer()).serializeToString(svgcopy)
    
    source = source.replace(/(\w+)?:?xlink=/g, 'xmlns:xlink=')
    source = source.replace(/NS\d+:href/g, 'xlink:href')
    blob = new Blob([ doctype + source], { type: 'image/svg+xml;charset=utf-8' })
    url = window.URL.createObjectURL(blob);
    if asSVG
        downloadBlob('chart.svg', url)
    else
        img = new HTML('img', { width: rect.width, height: rect.height, src: url})
        img.onload = () ->
            canvas = new HTML('canvas', { width: rect.width, height: rect.height})
            document.getElementById('chartWrapperHiddenMaster').appendChild(canvas)
            ctx = canvas.getContext('2d')
            ctx.drawImage(img, 0, 0)
            
            canvasUrl = canvas.toDataURL("image/png")
            downloadBlob('chart.png', canvasUrl)
            
        document.getElementById('chartWrapperHiddenMaster').appendChild(img)
    
rotateTable = (list) ->
    newList = []
    for x, i in list[0]
        arr = []
        for el in list
            arr.push(el[i])
        newList.push(arr)
    return newList
    
dataTable = (o) ->
    modal = new HTML('div', { class: "chartModal"})
    modalInner = new HTML('div', { class: "chartModalContent"})
    close = new HTML('span', {class: "chartModelClose", onclick: "this.parentNode.parentNode.parentNode.removeChild(this.parentNode.parentNode);"}, "X")
    modalInner.inject(close)
    modal.inject(modalInner)
    tbl = new HTML('table', { border: "1"})
    myList = o.config.data.columns
    if myList[0].length > myList.length
        myList = rotateTable(myList)
    for arr in myList
        tr = new HTML('tr')
        for el in arr
            if (el instanceof Date)
                el = el.toISOString().slice(0,10)
            td = new HTML('td', {}, String(el))
            tr.inject(td)
        tbl.inject(tr)
    modalInner.inject(tbl)
    document.body.appendChild(modal)


chartOnclick = (func, cid) ->
    xchart = xxCharts[cid]
    func(xchart)

switchChartType = (o, config, type) ->
    for k, v of config.data.types
        xtype = type
        m = type.match(/^(.+)\*$/)
        if m
            xtype = m[1] + v.split(/-/)[1]||v
        config.data.types[k] = xtype
    o.chartobj = c3.generate(config)
    
stackChart = (o, config, chart) ->
    arr = []
    for k, v of config.data.columns
        arr.push(v[0])

    if config.data.groups[0].length > 0
        config.data.groups = [[]]
        chart.groups([[]])
    else
        config.data.groups = [arr]
        chart.groups([arr])

class Chart
    constructor: (parent, type, data, options) ->
        cid = parseInt((Math.random()*1000000)).toString(16)
        @cid = cid
        
        xxCharts[cid] = this
        
        # Make main div wrapper
        @main = new HTML('div', { class: "chartWrapper"})
        @main.xThis = this
        @data = data
        
        # Make toolbar
        @toolbar = new HTML('div', {class: "chartToolbar"})
        @main.inject(@toolbar)
        
        # Title bar
        @titlebar = new HTML('div', {class: "chartTitle"}, if (options and options.title) then options.title else "")
        @main.inject(@titlebar)
        
        i = 0
        chartWrapperColors = genColors(16, 0.2, 0.75, true)
        
        # Default to generic buttons
        btns = chartWrapperButtons.generic.slice(0,999)
        
        # Line charts have more features than, say, donuts
        if type == 'line'
            for el in chartWrapperButtons.line
                btns.push(el)
                
        # Make the buttons appear
        @buttons = {}
        for btn in btns
            btnDiv = new HTML('div', { title: btn.title, class: "chartToolButton", style: { background: chartWrapperColors[i]} })
            inner = new HTML('i', { class: btn.icon })
            if btn.id
                @buttons[btn.id] = btnDiv
            btnDiv.inject(inner)
            @toolbar.inject(btnDiv)
            if btn.onclick
                do (btn, btnDiv) ->
                    btnDiv.addEventListener('click', () -> chartOnclick(btn.onclick, cid))
                
            i++
        
        # Make inner chart
        @chartdiv = new HTML('div', { class: "chartChart"})
        @main.inject(@chartdiv)
        
        if parent
            parent.appendChild(@main)
        else
            hObj = document.getElementById('chartWrapperHiddenMaster')
            if not hObj
                hObj = new HTML('div', { id: 'chartWrapperHiddenMaster', style: { visibility: "hidden"}})
                document.body.appendChild(hObj)
            hObj.appendChild(@main)
        
        if type == 'line'
            [@chartobj, @config] = charts_linechart(@chartdiv, data, options)
        if type == 'donut'
            [@chartobj, @config] = charts_donutchart(@chartdiv, data, 15)
         if type == 'gauge'
            [@chartobj, @config] = charts_gaugechart(@chartdiv, data)
        if type == 'radar'
            [@chartobj, @config] = charts_radarchart(@chartdiv, data)
         if type == 'relationship'
            [@chartobj, @config] = charts_linked(@chartdiv, data.nodes, data.links, options)
        
        # If this data source has distinguishable categories
        # show a checkbox to toggle it.
        if data.distinguishable
          id = Math.floor(Math.random() * 987654321).toString(16)
          chk = document.createElement('input')
          chk.setAttribute("type", "checkbox")
          chk.setAttribute("id", id)
          chk.style.marginLeft = '10px'
          if globArgs.distinguish and globArgs.distinguish == 'true'
                  chk.checked = true
          chk.addEventListener("change", () ->
                  distinguish = null
                  if this.checked
                          distinguish = 'true'
                          globArgs['distinguish'] = 'true'
                  
                  updateWidgets('line', null, { distinguish: distinguish })
                  updateWidgets('gauge', null, { distinguish: distinguish })
                  )
          @main.inject(mk('br'))
          @main.inject(chk)
          label = document.createElement('label')
          label.setAttribute("for", id)
          label.setAttribute("title", "Check this box to distinguish between sub-categories in this chart")
          chk.setAttribute("title", "Check this box to distinguish between sub-categories in this chart")
          label.style.paddingLeft = '5px'
          label.appendChild(document.createTextNode('Toggle category breakdown'))
          @main.inject(label)
        
        # If this data source has relative weightings
        # show a checkbox to toggle it.
        if data.relativeMode
          id = Math.floor(Math.random() * 987654321).toString(16)
          chk = document.createElement('input')
          chk.setAttribute("type", "checkbox")
          chk.setAttribute("id", id)
          chk.style.marginLeft = '10px'
          if globArgs.relative and globArgs.relative == 'true'
                  chk.checked = true
          chk.addEventListener("change", () ->
                  relative = null
                  if this.checked
                          relative = 'true'
                          globArgs['relative'] = 'true'
                  
                  updateWidgets('line', null, { relative: relative })
                  updateWidgets('gauge', null, { relative: relative })
                  )
          @main.inject(mk('br'))
          @main.inject(chk)
          label = document.createElement('label')
          label.setAttribute("for", id)
          label.setAttribute("title", "Check this box to use relative weighting")
          chk.setAttribute("title", "Check this box to use relative weighting")
          label.style.paddingLeft = '5px'
          label.appendChild(document.createTextNode('Toggle relative/comparative mode'))
          @main.inject(label)
          
        return @main
    
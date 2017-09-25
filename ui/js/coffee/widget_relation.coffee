relationship = (json, state) ->
        div = document.createElement('div')
        cats = new Array()
        dates = new Array()
        catdata = {}
        
        filled = { areaStyle: {type: 'default' } }
        if json.widgetType
          if json.widgetType.chartType
            type = json.widgetType.chartType
          if json.widgetType.stack
            stack = json.widgetType.stack
          if json.widgetType.nofill
            filled = null
        #if state.widget.args.representation
          #type = state.widget.args.representation
        
        if not state.widget.div.style.height
          div.style.minHeight = "900px"
        else
          div.style.minHeight = "100%"
        if state.widget.fullscreen
          div.style.minHeight = (window.innerHeight - 100) + "px"
        
        state.widget.inject(div, true)
        
        
        echartLine = echarts.init(div, theme);
        range = ""
        rect = div.getBoundingClientRect()
        colors = genColors(json.nodes.length+1, 0.6, 0.5, true)
        theme.textStyle.fontSize = Math.max(12, window.innerHeight/90)
        factor = Math.min(
          ((div.style.minHeight.match(/px/) && parseInt(div.style.minHeight)) || (div.style.height.match(/px/) && parseInt(div.style.height)) || window.innerHeight),
          ((div.style.minWidth.match(/px/) && parseInt(div.style.minWidth)) || (div.style.width.match(/px/) && parseInt(div.style.width)) || window.innerWidth)
          )
        for node, k in json.nodes
          node.draggable = true;
          node.itemStyle.normal.color = colors[k]
          node.x = (node.x/1000) * rect.width
          node.y = (node.y/1000) * rect.height
          node.symbolSize = (node.symbolSize/1000) * 0.8 * factor
          if location.href.match(/reltype=galaxy/)  or (state and state.config and state.config.reltype == 'galaxy')
            node.symbolSize = 0.01 * Math.min(div.style.minHeight.match(/px/) && parseInt(div.style.minHeight) || parseInt(div.style.height) || 500, window.innerWidth-100)
            node.x = node.y = null;
          if location.href.match(/reltype=circle/) or (state and state.config and state.config.reltype == 'circle')
            node.x = node.y = null;
            
        if location.href.match(/reltype=galaxy/) or (state and state.config and state.config.reltype == 'galaxy')
          for link in json.links
              link.lineStyle.normal.width = Math.max(Math.log2(link.lineStyle.normal.width), 1)
        for link in json.links
          link.lineStyle.normal.width *= factor/1000
        
        graph = {
          nodes: json.nodes,
          links: json.links
        }
        categories = [
          {name: "Foo"},
          {name: "Bar"}
        ]
        option = {
            title: {
                text: 'Project relationships',
                subtext: 'Commit volume and committers in common',
                top: 'bottom',
                left: 'right'
            },
            tooltip: {
              show: true,
              formatter: (params) => params.data.description || params.data.name
              },
            toolbox: {
              show: true,
              feature: {
                saveAsImage: {
                  show: true,
                  title: "Save Image"
                }
              }
            },
            legend: [{
                #selectedMode: 'single',
                data: categories.map( (a) => a.description )
            }],
            animationDuration: 1500,
            animationEasingUpdate: 'quinticInOut',
            series : [
                {
                    name: 'Project relationship',
                    type: 'graph',
                    layout: (if location.href.match(/reltype=galaxy/)  or (state and state.config and state.config.reltype == 'galaxy') then 'force' else (if location.href.match(/reltype=circle/)  or (state and state.config and state.config.reltype == 'circle') then 'circular' else 'none')),
                    data: graph.nodes,
                    links: graph.links,
                    categories: categories,
                    roam: true,
                    label: {
                        normal: {
                            position: 'bottom',
                            formatter: '{b}',
                            color: "black",
                            textStyle: {
                              color: 'rgba(0,0,0,1)',
                              fontSize: Math.max(12, window.innerHeight/90)
                            }
                        }
                    },
                    lineStyle: {
                        normal: {
                            color: 'source',
                            curveness: if location.href.match(/reltype=galaxy/)  or (state and state.config and state.config.reltype == 'galaxy') then 0 else 0.3
                        }
                    },
                    force: if location.href.match(/reltype=galaxy/)  or (state and state.config and state.config.reltype == 'galaxy') then { repulsion: 75 } else {}
                }
            ]
        };
        echartLine.setOption(option);
        
        if not json.widget
          tName = 'reltype'
          list = document.createElement('select')
          list.setAttribute("data", tName)
          state.widget.inject(mk('br'))
          state.widget.inject(txt("Display mode: "))
          state.widget.inject(list)
          
          for item in ['standard', 'galaxy', 'circle']
              opt = document.createElement('option')
              opt.value = item
              opt.text = item
              if (globArgs[tName] and globArgs[tName] == item)
                  opt.selected = 'selected'
              list.appendChild(opt)
          
          list.addEventListener("change", () ->
                  source = this.value
                  if source == ""
                          source = null
                  tName = this.getAttribute("data")
                  globArgs[tName] = source
                  x = {}
                  x[tName] = source
                  updateWidgets('relationship', null, x)                      
          , false)
        
          p = mk('p', {}, "#{json.nocon} connections found, highest connection count is #{json.maxcon}, average is #{json.avgcon} across all #{json.nodes.length} projects.")
          state.widget.inject(p)
            
        
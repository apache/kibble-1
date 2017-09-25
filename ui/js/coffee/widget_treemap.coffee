treemap = (json, state) ->
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
        if not json.widget.title or json.widget.title.length == 0
          json.widget.title = 'Languages'
          
        if not state.widget.div.style.height
          div.style.minHeight = "900px"
        else
          div.style.minHeight = "100%"
        if state.widget.fullscreen
          div.style.minHeight = (window.innerHeight - 100) + "px"
        
        state.widget.inject(div, true)
        
        
        
        range = ""
        rect = div.getBoundingClientRect()
        theme.color = genColors(json.treemap.length+1, 0.6, 0.5, true)
        colors = genColors(json.treemap.length+1, 0.6, 0.5, true)
        theme.textStyle.fontSize = Math.max(12, window.innerHeight/100)
        echartLine = echarts.init(div, theme);
        
        ld = []
        for lang, i in json.treemap
          ld.push(lang)
          for project in lang
            project.color = colors[i]
            project.itemStyle = {
              normal: {
                color: colors[i]
              }
            }
        
        option = {

            title: {
                text: json.widget.title,
                left: 'center'
            },
            legend: [{
              x: 'center',
              y: 'top',
                #selectedMode: 'single',
              data: ld
            }],
    
            tooltip: {
                show: true,
                feature: {
                  saveAsImage: {
                    show: true,
                    title: "Save Image"
                  }
                },
                formatter: (info) ->
                    value = info.value;
                    treePathInfo = info.treePathInfo;
                    treePath = [];
    
                    for i in [1...treePathInfo.length]
                        treePath.push(treePathInfo[i].name)
                    
    
                    return [
                        '<div class="tooltip-title">' + treePath.join('/') + '</div>',
                        'Lines of Code: ' + value.pretty(),
                    ].join('');
                
            },
        
            series: [
                {
                    name:json.widget.title,
                    type:'treemap',
                    visibleMin: 1000,
                    label: {
                        show: true,
                        formatter: '{b}'
                    },
                    itemStyle: {
                        normal: {
                            borderColor: '#fff'
                        }
                    },
                    levels: [{
                              itemStyle: {
                                  normal: {
                                      borderColor: '#555',
                                      borderWidth: 4,
                                      gapWidth: 4
                                  }
                              }
                          },
                          {
                              colorSaturation: [0.3, 0.6],
                              itemStyle: {
                                  normal: {
                                      borderColorSaturation: 0.7,
                                      gapWidth: 2,
                                      borderWidth: 2
                                  }
                              }
                          }
                        ],
                    data: json.treemap
                }
            ]
        }
        echartLine.setOption(option = option);
          
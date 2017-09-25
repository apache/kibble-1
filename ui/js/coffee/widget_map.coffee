# Donut widget
worldmap = (json, state) ->
        
    dt = []
    dtl = []
    l = 0
    tot = 0
    ttot = 0
    top = []
    cmax = 0;
    ctotal = 0
    if json.countries
        for item, details of json.countries
            dt.push({name: details.name, value: details.count})
            ctotal += details.count
            if details.count > cmax
                cmax = details.count
        
    lmain = document.createElement('div')
    radius = ['30%', '50%']
    if not state.widget.div.style.height
        lmain.style.height = "500px"
    else
        lmain.style.height = "100%"
    if state.widget.fullscreen
        lmain.style.height = "1000px"
        radius = ['35%', '60%']
        theme.textStyle.fontSize = 20
    lmain.style.width = "100%"
    state.widget.inject(lmain, true)
    echartMap = echarts.init(lmain, theme);
    
    echartMap.setOption({
      title: {
            text: "Worldwide distribution by country"
            subtext: "(" + ctotal.pretty() + " in total from " + (json.numberOfCountries||0) + " countries)"
          }
      calculable: true,
      dataRange: {
                min: 0,
                max: cmax,
                text:['High','Low'],
                realtime: false,
                calculable : true,
                color: ['orangered','yellow','lightskyblue']
            },
      toolbox: {
        show: true,
        feature: {
          dataView : {show: true, title: 'Data view', readOnly: false, lang: ['Data View', 'Close', 'Update']},
          restore: {
            show: true,
            title: "Restore"
          },
          saveAsImage: {
            show: true,
            title: "Save Image"
          }
        }
      },
      tooltip: {
        trigger: 'item',
        formatter: (params) ->
            return params.seriesName + '<br/>' + params.name + ' : ' + (params.value||0).pretty();
        
    },
      
      series: [{
        name: state.widget.name,
        type: 'map',
        mapType: 'world',
        mapLocation: {
                y : 60
            }
        itemStyle: {
          emphasis:{label:{show:true}}
        },
        data: dt
      }]
    });
    theme.textStyle.fontSize = 12
      
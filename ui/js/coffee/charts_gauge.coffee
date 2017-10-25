charts_gaugechart = (obj, data) ->
    if data.gauge
        data = data.gauge
    
    config = {
        bindto: obj,
        data: {
          columns: [[data.key or 'value', data.value or data]],
          type: 'gauge'
        },
        gauge: {
            min: 0,
            max: 100
            },
        color: {
            pattern: ['#FF0000', '#F97600', '#F6C600', '#60B044'],
            threshold: {
                values: [25, 55, 80, 100]
            }
        },
        tooltip: {
            format: {
                value: (val) => d3.format(',')(val)
            }
        }
    }
    c = c3.generate(config)
    return [c, config]


gauge = (json, state) ->
        
    lmain = new HTML('div')
    state.widget.inject(lmain, true)
    
    if json.gauge and json.gauge.text
        lmain.inject(new HTML('p', {}, json.gauge.text))
    
    gaugeChart = new Chart(lmain, 'gauge', json)


charts_linechart_stacked = (o,d) => charts_linechart(o,d,'area-spline', true)

charts_linechart = (obj, data, options) ->
    linetype = if (options and options.linetype) then options.linetype else 'line'
    stacked = if (options and options.stacked) then options.stacked else false
    if options and options.filled and linetype == "line"
        linetype = "area-spline"
    a = 0 # Number of segments
    asDataArray = []
    asList = []
    asTypes = []
    axisData = {
        y: {
                tick: {
                    format: d3.format('s')
                }
            }
    }
    if data.timeseries and isArray(data.timeseries)
        dateFormat = '%Y-%m-%d'
        if data.histogram and data.histogram == 'quarterly'
            dateFormat = (x) => "Q" + ([1,2,3,4][Math.floor(x.getMonth()/3)]) + ", " + x.getFullYear()
        if data.histogram and data.histogram == 'monthly'
            dateFormat = '%b, %Y'
        if data.histogram and data.histogram == 'yearly'
            dateFormat = '%Y'
        ts = [
            ['x']
            ]

        # Get all timestamps
        
        xts = {}
        for el in data.timeseries
            axisData.x = {
                    type: 'timeseries',
                    tick: {
                        format: dateFormat
                    }
                }
            
            ndate = new Date(parseInt(el.date)*1000.0)
            ts[0].push(ndate)
            for k, v of el
                if k != 'date'
                    if k == 'deletions'
                        v = -v
                    if xts[k] == undefined
                        xts[k] = []
                    xts[k].push(v)
                    
        for key, val of xts
            xx = [key]
            for el in val
                xx.push(el)
            ts.push(xx)
            asList.push(key)
            asTypes[key] = linetype
            a++
                
        asDataArray = ts
    else
        for k, v of data
            asList.push(k)
            asTypes[k] = linetype
            tmpArray = [k]
            for dataPoint in v
                tmpArray.push(dataPoint)
            asDataArray.push(tmpArray)
            a++
    config = {
        bindto: obj,
        data: {
          x: 'x',
          #xFormat: '%s',
          columns: asDataArray,
          types: asTypes,
          groups: if stacked then [asList] else [[]]
        },
        axis: axisData,
        color: {
            pattern: genColors(a + 1, 0.55, 0.475, true)
            },
        subchart: {
          show: false
        },
        point: {
            show: false
        },
        bar: {
            width: {
                ratio: 0.7
            }
        }
        tooltip: {
            format: {
                value: (val) => d3.format(',')(val)
            }
        }
    }
    c = c3.generate(config)
    return [c, config]

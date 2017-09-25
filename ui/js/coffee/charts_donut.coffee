charts_donutchart = (obj, data, maxN) ->
    a = 0 # Number of segments
    asDataArray = []
    if data.counts
        data = data.counts
    for k, v of data
        asDataArray.push([k,v])
        a++
    asDataArray.sort((a,b) => b[1] - a[1])
    if maxN and asDataArray.length > maxN
        others = 0
        narr = asDataArray.slice(maxN, asDataArray.length-maxN)
        asDataArray = asDataArray.slice(0,maxN)
        for el in narr
            others += el[1]
        asDataArray.push(['Others', others])
        asDataArray.sort((a,b) => b[1] - a[1])
    config = {
        bindto: obj,
        data: {
          columns: asDataArray,
          type: 'donut'
        },
        donut: {
            #title: "foo"
            width: 50
        },
        color: {
            pattern: genColors(a + 1, 0.55, 0.475, true)
            },
        tooltip: {
            format: {
                value: (val) => d3.format(',')(val)
            }
        }
    }
    c = c3.generate(config)
    return [c, config]

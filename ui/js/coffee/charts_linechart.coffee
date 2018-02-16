#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
        if data.interval and data.interval == 'hour'
            dateFormat = '%Y-%m-%d %H:%M'
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
        for k, v of data.counts
            asList.push(k)
            asTypes[k] = 'bar'
            tmpArray = [k]
            if isArray(v)
                for dataPoint in v
                    tmpArray.push(dataPoint)
            else
                tmpArray.push(v)
            asDataArray.push(tmpArray)
            a++
    config = {
        bindto: obj,
        data: {
          x: if data.timeseries then 'x' else null,
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

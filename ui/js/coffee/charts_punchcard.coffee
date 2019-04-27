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

punchcard_color = (p, MAX) ->
    v = (p/MAX)
    hue=((1-v)*120).toString(10)
    return "hsl(#{hue},80%,40%)"


pval = (d,m) ->
    v = Math.max(d, m/3)
    if v > m/3
        v = (v+(m/3)) / m
    else
        v = 0.33

charts_punchcard = (obj, data, options) ->
    div = document.getElementById('tooltip_punchcard')
    if not div
        div = d3.select("body").append("div").attr("class", "punchcard_tooltip").attr('id', 'tooltip_punchcard').style("opacity", 0)
    else
        div = d3.select(div)
    data = data.timeseries
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    c = []

    chart = d3.select(obj).append("svg").attr("width", '100%').attr("height", '100%')
    
    
    MAX = 0
    for k, v of data
        m = k.split(/ - /)
        a = m[0]
        b = m[1]
        ypos = 0
        if b == '24'
            b = 0
        xpos = 0.1 + (parseInt(b) ) * (0.036)
        for n,d of days
            if d == a
                ypos = 0.04 + (n * 0.10)
        c.push({x: xpos, y: ypos, r: v, h: "<span style='font-size:0.9rem;'>#{a}, #{b}:00 -> #{(parseInt(b)+1) % 24}:00 UTC</span><br/>"})
        MAX = Math.max(MAX, v)
    circles = chart.selectAll('svg').data(c).enter().append("circle");
    labels = chart.selectAll('svg').data(days).enter().append('text')
    slots = chart.selectAll('svg').data([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]).enter().append('text')
    
    
    redraw = () ->
        xy = obj.getBoundingClientRect()
        xy.height = xy.width * 0.5
        chart.attr('width', xy.width + 'px')
        chart.attr('height', xy.height + 'px')
        maxr = Math.sqrt(xy.width**2 + xy.height**2) / 80
        cw = (0.03*xy.width)
        circles.attr("cx", (d) => (d.x*xy.width) + cw/2).attr("cy", (d) => 50 + d.y*xy.height ).attr("r", (d) => pval(d.r, MAX) * maxr).style("fill", (d) => punchcard_color(d.r, MAX)).
        on("mouseover", (d) -> 
            div.transition()
                .duration(200)		
                .style("opacity", .9)
            div	.html(d.h + d.r.pretty() + " commits")	
                .style("left", (d3.event.pageX) + "px")		
                .style("top", (d3.event.pageY - 28) + "px");
        ).on("mouseout", (d) ->
            div.transition()
                .duration(200)		
                .style("opacity", 0)
            )
        labels.attr('x', 20).attr('y', (d) => (55 + (0.04 + days.indexOf(d) * 0.10) * xy.height)).attr('font-size', maxr*1.75).text((d) => d)
        slots.attr('x', (d) => (0.1 + d * 0.036) * xy.width + cw/2).attr('y',38).attr('text-anchor', 'middle').attr('width', cw).attr('font-size', maxr*1.5).text((d) => d)
    chart.node().addEventListener("resize", redraw)
    window.addEventListener("resize", redraw)
    redraw();
    
    return [chart, {punchcard: true}]


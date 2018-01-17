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

datepickers = {}

updateTimeseriesWidgets = (range) ->
        if range
            from = range[0]
            to = range[1]
            globArgs.from = from
            globArgs.to = to
            updateWidgets('line', null, { to: to, from: from})
            updateWidgets('top5', null, { to: to, from: from})
            updateWidgets('factors', null, { to: to, from: from})
            updateWidgets('trends', null, { to: to, from: from})
            updateWidgets('donut', null, { to: to, from: from})
            updateWidgets('gauge', null, { to: to, from: from})
            updateWidgets('radar', null, { to: to, from: from})
            updateWidgets('relationship', null, { to: to, from: from})
            updateWidgets('treemap', null, { to: to, from: from})
            updateWidgets('report', null, { to: to, from: from})
            updateWidgets('mvp', null, { to: to, from: from})
            updateWidgets('comstat', null, { to: to, from: from})
            updateWidgets('worldmap', null, { to: to, from: from})
            updateWidgets('jsondump', null, { to: to, from: from})
                
datepicker = (widget) ->
        div = document.createElement('div')
        div.setAttribute("class", "well")
        form = document.createElement('form')
        div.appendChild(form)
        fieldset = document.createElement('fieldset')
        form.appendChild(fieldset)
        cgroup = document.createElement('div')
        cgroup.setAttribute("class", "control-group")
        fieldset.appendChild(cgroup)
        controls = document.createElement('div')
        controls.setAttribute("class", "controls")
        cgroup.appendChild(controls)
        group = document.createElement('div')
        group.setAttribute("class", "input-prepend input-group")
        controls.appendChild(group)
        span = document.createElement('span')
        span.setAttribute("class", "add-on input-group-addon")
        group.appendChild(span)
        i = document.createElement('i')
        i.setAttribute("class", "glyphicon glyphicon-calendar fa fa-calendar")
        span.appendChild(i)
        input = document.createElement('input')
        input.setAttribute("type", "text")
        input.style.width = "240px"
        input.setAttribute("name", "date")
        input.setAttribute("class", "form-control")
        now = (if globArgs.from then moment(parseInt(globArgs.from)*1000) else moment().subtract(6, 'months')).format('YYYY-MM-DD') + " to " + (if globArgs.from then moment(parseInt(globArgs.to)*1000) else moment()).format('YYYY-MM-DD')
        input.setAttribute("value", now)
        id = Math.floor(Math.random()*987654321).toString(16)
        input.setAttribute("id", id)
        group.appendChild(input)
        
        widget.inject(div)
        
        
        datePickerOptions = {
          startDate: if globArgs.from then moment(new Date(globArgs.from*1000)) else moment().subtract(6, 'months'),
          endDate: if globArgs.to then moment(new Date(globArgs.to*1000)) else moment(),
          minDate: '1970-01-01',
          maxDate: '2020-01-01',
          dateLimit: {
            days: 365
          },
          showDropdowns: true,
          showWeekNumbers: true,
          timePicker: false,
          timePickerIncrement: 1,
          timePicker12Hour: true,
          ranges: {
            'Today': [moment(), moment()],
            'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
            'Past Week': [moment().subtract(7, 'days'), moment().subtract(1, 'days')],
            'Past 30 Days': [moment().subtract(30, 'days'), moment().subtract(1, 'days')],
            'This Month': [moment().startOf('month'), moment().endOf('month')],
            'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')],
            'Last 3 Months': [moment().subtract(3, 'month'), moment()],
            'Last 6 Months': [moment().subtract(6, 'month'), moment()],
            'Last 12 Months': [moment().subtract(1, 'year'), moment()],
            'Last 2 Years': [moment().subtract(2, 'year'), moment()],
            'Last 5 Years': [moment().subtract(5, 'year'), moment()],
            'Last 10 Years': [moment().subtract(10, 'year'), moment()],
            'Last...Snoot Years': [moment(42300, 'X'), moment()]
          },
          opens: 'left',
          buttonClasses: ['btn btn-default'],
          applyClass: 'btn-small btn-primary',
          cancelClass: 'btn-small',
          format: 'YYYY-MM-DD',
          separator: ' to ',
          locale: {
            applyLabel: 'Submit',
            cancelLabel: 'Clear',
            fromLabel: 'From',
            toLabel: 'To',
            customRangeLabel: 'Custom',
            daysOfWeek: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
            monthNames: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
            firstDay: 1
          }
        };
        
        $('#' + id).daterangepicker(datePickerOptions, (start, end, label) ->
                console.log(start._d.getTime()/1000)
                updateTimeseriesWidgets([Math.floor(start._d.getTime()/1000), Math.floor(end._d.getTime()/1000)])
        );


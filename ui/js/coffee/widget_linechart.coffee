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

linechart = (json, state) ->
        div = document.createElement('div')
        if json.text
                div.inject(new HTML('p', {}, json.text))
        cats = new Array()
        dates = new Array()
        catdata = {}
        if not isArray(json.timeseries) and not json.counts
          div.innerHTML = "No data available"
          state.widget.inject(div, true)
          return
        if json.timeseries
                json.timeseries.sort((a,b) => a.date - b.date)
                for point in json.timeseries
                  for key, val of point
                    if key != 'date' and not (key in cats)
                      cats.push(key)
                      catdata[key] = new Array()
                
                for point in json.timeseries
                  m = moment(point.date*1000)
                  rv = m.format("MMM, YYYY")
                  
                  if json.histogram == "daily" || json.interval == 'day'
                    rv =  m.format("MMMM DD, YYYY")
                  if json.interval == 'year'
                    rv = m.format("YYYY")
                  else if json.interval == 'quarter'
                    rv = "Q" +m.format("Q, YYYY")
                  else if json.interval == 'week'
                    rv = "Week " +m.format("W, YYYY")
                  dates.push (rv)
                  for key, val of point
                    if key != 'date'
                      if key == 'deletions'
                        val = -val
                      catdata[key].push(val)
                  for cat in cats
                    if not cat in point
                      catdata[cat].push(0)
              
        catseries = []
        type = 'spline'
        stack = false
        filled = true
        if json.widgetType
          if json.widgetType.chartType
            type = json.widgetType.chartType
          if json.widgetType.stack
            stack = json.widgetType.stack
          if json.widgetType.nofill
            filled = null
        if state and state.config
          if state.config.charttype
            if state.config.charttype == 'line'
              type = 'line'
              stack = false
              if not state.config.fill
                filled = null
            if state.config.stack
              stack = true
        #if state.widget.args.representation
          #type = state.widget.args.representation
       
        if not state.widget.div.style.height
          div.style.minHeight = "280px"
        else
          div.style.minHeight = "100%"
        if state.widget.fullscreen
          div.style.minHeight = "640px"
        
        
        state.widget.inject(div, true)
        
        
        range = ""
        if state.widget.args.daterangeRaw
                from = new Date(state.widget.args.daterangeRaw[0]*1000).toDateString()
                to = new Date(state.widget.args.daterangeRaw[1]*1000).toDateString()
                range = "between " + from + " and " + to
        
        chartBox = new Chart(div, 'line', json, {title: range, stacked: stack, linetype: type, filled: filled})
        if state.widget.args.source == 'git-evolution'
          # Checkbox for lang breakdown
          id = Math.floor(Math.random() * 987654321).toString(16)
          chk = document.createElement('input')
          chk.setAttribute("type", "checkbox")
          chk.setAttribute("id", id)
          chk.style.marginLeft = '10px'
          if globArgs.extended and globArgs.extended == 'true'
                  chk.checked = true
          chk.addEventListener("change", () ->
                  extended = null
                  if this.checked
                          extended = 'true'
                          globArgs['extended'] = 'true'
                  
                  updateWidgets('line', null, { extended: extended })
                  )
          state.widget.inject(mk('br'))
          state.widget.inject(chk)
          label = document.createElement('label')
          label.setAttribute("for", id)
          label.setAttribute("title", "Check this box to view evolutionary breakdown of languages")
          chk.setAttribute("title", "Check this box to view evolutionary breakdown of languages")
          label.style.paddingLeft = '5px'
          label.appendChild(document.createTextNode('Toggle language breakdown'))
          state.widget.inject(label)
          
          # Checkbox for discounting markups/docs/build-files
          if globArgs.extended
            id = Math.floor(Math.random() * 987654321).toString(16)
            chk = document.createElement('input')
            chk.setAttribute("type", "checkbox")
            chk.setAttribute("id", id)
            chk.style.marginLeft = '10px'
            if globArgs.codeonly and globArgs.codeonly == 'true'
                    chk.checked = true
            chk.addEventListener("change", () ->
                    codeonly = null
                    if this.checked
                            codeonly = 'true'
                            globArgs['codeonly'] = 'true'
                    
                    updateWidgets('line', null, { codeonly: codeonly })
                    )
            state.widget.inject(chk)
            label = document.createElement('label')
            label.setAttribute("for", id)
            label.setAttribute("title", "Check this box to show only programming languages (no docs/markups/build-configs)")
            chk.setAttribute("title", "Check this box to show only programming languages (no docs/markups/build-configs)")
            label.style.paddingLeft = '5px'
            label.appendChild(document.createTextNode('Only show programming languages'))
            state.widget.inject(label)
            
        if (not state.public) and json.interval
          tName = 'interval'
          list = document.createElement('select')
          list.setAttribute("data", tName)
          state.widget.inject(mk('br'))
          state.widget.inject(txt("Select interval: "))
          state.widget.inject(list)
          histograms = ['day','week','month','quarter','year']
          # Some charts may require finer grained precision (CI Queues etc)
          if state.widget.wargs and state.widget.wargs.histogram == 'hour'
                histograms.unshift('hour')
          for item in histograms
              opt = document.createElement('option')
              opt.value = item
              opt.text = item
              if (globArgs[tName] and globArgs[tName] == item) or json.interval == item
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
                  updateWidgets('line', null, x)                      
          , false)

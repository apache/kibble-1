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

API = 2

Number.prototype.pretty = (fix) ->
    if (fix)
        return String(this.toFixed(fix)).replace(/(\d)(?=(\d{3})+\.)/g, '$1,');
    return String(this.toFixed(0)).replace(/(\d)(?=(\d{3})+$)/g, '$1,');


fetch = (url, xstate, callback, nocreds) ->
    xmlHttp = null;
    # Set up request object
    if window.XMLHttpRequest
        xmlHttp = new XMLHttpRequest();
    else
        xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
    if not nocreds
        xmlHttp.withCredentials = true
    # GET URL
    xmlHttp.open("GET", "api/#{url}", true);
    xmlHttp.send(null);
    
    xmlHttp.onreadystatechange = (state) ->
            if xmlHttp.readyState == 4 and xmlHttp.status == 500
                if snap
                    snap(xstate)
                return
            if xmlHttp.readyState == 4 and xmlHttp.status >= 400
                js = JSON.parse(xmlHttp.responseText)
                # If we need to log in first, redirect to login page
                if js.code == 403
                    mpart = location.href.match(/\/\/[^/]+\/(.+)$/)[1]
                    location.href = "login.html?redirect=" + mpart
                badModal(js.reason)
                return
            if xmlHttp.readyState == 4 and xmlHttp.status == 200
                if callback
                    # Try to parse as JSON and deal with cache objects, fall back to old style parse-and-pass
                    try
                        response = JSON.parse(xmlHttp.responseText)
                        callback(response, xstate);
                    catch e
                        callback(JSON.parse(xmlHttp.responseText), xstate)

put = (url, json, xstate, callback, nocreds = false) ->
    xmlHttp = null;
    # Set up request object
    if window.XMLHttpRequest
        xmlHttp = new XMLHttpRequest();
    else
        xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
    if not nocreds
        xmlHttp.withCredentials = true
    # GET URL
    xmlHttp.open("PUT", "api/#{url}", true);
    xmlHttp.send(JSON.stringify(json || {}));
    
    xmlHttp.onreadystatechange = (state) ->
            if xmlHttp.readyState == 4 and xmlHttp.status == 500
                if snap
                    snap(xstate)
                return
            if xmlHttp.readyState == 4 and xmlHttp.status >= 400
                js = JSON.parse(xmlHttp.responseText)
                badModal(js.reason)
                return
            if xmlHttp.readyState == 4 and xmlHttp.status == 200
                if callback
                    # Try to parse as JSON and deal with cache objects, fall back to old style parse-and-pass
                    try
                        response = JSON.parse(xmlHttp.responseText)
                        if response && response.loginRequired
                            location.href = "/login.html"
                            return
                        callback(response, xstate);
                    catch e
                        callback(JSON.parse(xmlHttp.responseText), xstate)


patch = (url, json, xstate, callback, nocreds = false) ->
    xmlHttp = null;
    # Set up request object
    if window.XMLHttpRequest
        xmlHttp = new XMLHttpRequest();
    else
        xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
    if not nocreds
        xmlHttp.withCredentials = true
    # GET URL
    xmlHttp.open("PATCH", "api/#{url}", true);
    xmlHttp.send(JSON.stringify(json || {}));
    
    xmlHttp.onreadystatechange = (state) ->
            if xmlHttp.readyState == 4 and xmlHttp.status == 500
                if snap
                    snap(xstate)
                return
            if xmlHttp.readyState == 4 and xmlHttp.status >= 400
                js = JSON.parse(xmlHttp.responseText)
                badModal(js.reason)
                return
            if xmlHttp.readyState == 4 and xmlHttp.status == 200
                if callback
                    # Try to parse as JSON and deal with cache objects, fall back to old style parse-and-pass
                    try
                        response = JSON.parse(xmlHttp.responseText)
                        if response && response.loginRequired
                            location.href = "/login.html"
                            return
                        callback(response, xstate);
                    catch e
                        callback(JSON.parse(xmlHttp.responseText), xstate)

xdelete = (url, json, xstate, callback, nocreds = false) ->
    xmlHttp = null;
    # Set up request object
    if window.XMLHttpRequest
        xmlHttp = new XMLHttpRequest();
    else
        xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
    if not nocreds
        xmlHttp.withCredentials = true
    # GET URL
    xmlHttp.open("DELETE", "api/#{url}", true);
    xmlHttp.send(JSON.stringify(json || {}));
    
    xmlHttp.onreadystatechange = (state) ->
            if xmlHttp.readyState == 4 and xmlHttp.status == 500
                if snap
                    snap(xstate)
                return
            if xmlHttp.readyState == 4 and xmlHttp.status >= 400
                js = JSON.parse(xmlHttp.responseText)
                badModal(js.reason)
                return
            if xmlHttp.readyState == 4 and xmlHttp.status == 200
                if callback
                    # Try to parse as JSON and deal with cache objects, fall back to old style parse-and-pass
                    try
                        response = JSON.parse(xmlHttp.responseText)
                        if response && response.loginRequired
                            location.href = "/login.html"
                            return
                        callback(response, xstate);
                    catch e
                        callback(JSON.parse(xmlHttp.responseText), xstate)


post = (url, json, xstate, callback, snap) ->
    xmlHttp = null;
    # Set up request object
    if window.XMLHttpRequest
        xmlHttp = new XMLHttpRequest();
    else
        xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
    xmlHttp.withCredentials = true
    # Construct form data
    for key, val of json
        if val.match
            if val.match(/^\d+$/)
                json[key] = parseInt(val)
            if val == 'true'
                json[key] = true
            if val == 'false'
                json[key] = false
    fdata = JSON.stringify(json)
    
    # POST URL
    xmlHttp.open("POST", "api/#{url}", true);
    xmlHttp.setRequestHeader("Content-type", "application/json");
    xmlHttp.send(fdata);
    
    xmlHttp.onreadystatechange = (state) ->
            if xmlHttp.readyState == 4 and xmlHttp.status == 500
                if snap
                    snap(xstate)
            if xmlHttp.readyState == 4 and xmlHttp.status == 200
                if callback
                    # Try to parse as JSON and deal with cache objects, fall back to old style parse-and-pass
                    try
                        response = JSON.parse(xmlHttp.responseText)
                        if xstate and xstate.widget
                                    xstate.widget.json = response
                        callback(response, xstate);
                    catch e
                        callback(JSON.parse(xmlHttp.responseText), xstate)

mk = (t, s, tt) ->
    r = document.createElement(t)
    if s
        for k, v of s
            if v
                r.setAttribute(k, v)
    if tt
        if typeof tt == "string"
            app(r, txt(tt))
        else
            if isArray tt
                for k in tt
                    if typeof k == "string"
                        app(r, txt(k))
                    else
                        app(r, k)
            else
                app(r, tt)
    return r

app = (a,b) ->
    if isArray b
        for item in b
            if typeof item == "string"
                item = txt(item)
            a.appendChild(item)
    else
        return a.appendChild(b)


set = (a, b, c) ->
    return a.setAttribute(b,c)

txt = (a) ->
    return document.createTextNode(a)

get = (a) ->
    return document.getElementById(a)

swi = (obj) ->
    switchery = new Switchery(obj, {
                color: '#26B99A'
            })

cog = (div, size = 200) ->
        idiv = document.createElement('div')
        idiv.setAttribute("class", "icon")
        idiv.setAttribute("style", "text-align: center; vertical-align: middle; height: 500px;")
        i = document.createElement('i')
        i.setAttribute("class", "fa fa-spin fa-cog")
        i.setAttribute("style", "font-size: " + size + "pt !important; color: #AAB;")
        idiv.appendChild(i)
        idiv.appendChild(document.createElement('br'))
        idiv.appendChild(document.createTextNode('Loading, hang on tight..!'))
        div.innerHTML = ""
        div.appendChild(idiv)

globArgs = {}


theme = {
          color: [],

          title: {
              itemGap: 8,
              textStyle: {
                  fontWeight: 'normal',
                  color: '#408829'
              }
          },

          dataRange: {
              color: ['#1f610a', '#97b58d']
          },

          toolbox: {
              color: ['#408829', '#408829', '#408829', '#408829']
          },

          tooltip: {
              backgroundColor: 'rgba(0,0,0,0.5)',
              axisPointer: {
                  type: 'line',
                  lineStyle: {
                      color: '#408829',
                      type: 'dashed'
                  },
                  crossStyle: {
                      color: '#408829'
                  },
                  shadowStyle: {
                      color: 'rgba(200,200,200,0.3)'
                  }
              }
          },

          dataZoom: {
              dataBackgroundColor: '#eee',
              fillerColor: 'rgba(64,136,41,0.2)',
              handleColor: '#408829'
          },
          grid: {
              borderWidth: 0
          },

          categoryAxis: {
              axisLine: {
                  lineStyle: {
                      color: '#408829'
                  }
              },
              splitLine: {
                  lineStyle: {
                      color: ['#eee']
                  }
              }
          },

          valueAxis: {
              axisLine: {
                  lineStyle: {
                      color: '#408829'
                  }
              },
              splitArea: {
                  show: true,
                  areaStyle: {
                      color: ['rgba(250,250,250,0.1)', 'rgba(200,200,200,0.1)']
                  }
              },
              splitLine: {
                  lineStyle: {
                      color: ['#eee']
                  }
              }
          },
          timeline: {
              lineStyle: {
                  color: '#408829'
              },
              controlStyle: {
                  normal: {color: '#408829'},
                  emphasis: {color: '#408829'}
              }
          },

          k: {
              itemStyle: {
                  normal: {
                      color: '#68a54a',
                      color0: '#a9cba2',
                      lineStyle: {
                          width: 1,
                          color: '#408829',
                          color0: '#86b379'
                      }
                  }
              }
          },
          map: {
              itemStyle: {
                  normal: {
                      areaStyle: {
                          color: '#ddd'
                      },
                      label: {
                          textStyle: {
                              color: '#c12e34'
                          }
                      }
                  },
                  emphasis: {
                      areaStyle: {
                          color: '#99d2dd'
                      },
                      label: {
                          textStyle: {
                              color: '#c12e34'
                          }
                      }
                  }
              }
          },
          force: {
              itemStyle: {
                  normal: {
                      linkStyle: {
                          strokeColor: '#408829'
                      }
                  }
              }
          },
          chord: {
              padding: 4,
              itemStyle: {
                  normal: {
                      lineStyle: {
                          width: 1,
                          color: 'rgba(128, 128, 128, 0.5)'
                      },
                      chordStyle: {
                          lineStyle: {
                              width: 1,
                              color: 'rgba(128, 128, 128, 0.5)'
                          }
                      }
                  },
                  emphasis: {
                      lineStyle: {
                          width: 1,
                          color: 'rgba(128, 128, 128, 0.5)'
                      },
                      chordStyle: {
                          lineStyle: {
                              width: 1,
                              color: 'rgba(128, 128, 128, 0.5)'
                          }
                      }
                  }
              }
          },
          gauge: {
              startAngle: 225,
              endAngle: -45,
              axisLine: {
                  show: true,
                  lineStyle: {
                      color: [[0.2, '#86b379'], [0.8, '#68a54a'], [1, '#408829']],
                      width: 8
                  }
              },
              axisTick: {
                  splitNumber: 10,
                  length: 12,
                  lineStyle: {
                      color: 'auto'
                  }
              },
              axisLabel: {
                  textStyle: {
                      color: 'auto'
                  }
              },
              splitLine: {
                  length: 18,
                  lineStyle: {
                      color: 'auto'
                  }
              },
              pointer: {
                  length: '90%',
                  color: 'auto'
              },
              title: {
                  textStyle: {
                      color: '#333'
                  }
              },
              detail: {
                  textStyle: {
                      color: 'auto'
                  }
              }
          },
          textStyle: {
              fontFamily: 'Arial, Verdana, sans-serif'
          }
      };

isArray = ( value ) ->
    value and
        typeof value is 'object' and
        value instanceof Array and
        typeof value.length is 'number' and
        typeof value.splice is 'function' and
        not ( value.propertyIsEnumerable 'length' )
        

### isHash: function to detect if an object is a hash ###
isHash = (value) ->
    value and
        typeof value is 'object' and
        not isArray(value)
        

class HTML
    constructor: (type, params, children) ->
        ### create the raw element, or clone if passed an existing element ###
        if typeof type is 'object'
            @element = type.cloneNode()
        else
            @element = document.createElement(type)
        
        ### If params have been passed, set them ###
        if isHash(params)
            for key, val of params
                ### Standard string value? ###
                if typeof val is "string" or typeof val is 'number'
                    @element.setAttribute(key, val)
                else if isArray(val)
                    ### Are we passing a list of data to set? concatenate then ###
                    @element.setAttribute(key, val.join(" "))
                else if isHash(val)
                    ### Are we trying to set multiple sub elements, like a style? ###
                    for subkey,subval of val
                        if not @element[key]
                            throw "No such attribute, #{key}!"
                        @element[key][subkey] = subval
        
        ### If any children have been passed, add them to the element  ###
        if children
            ### If string, convert to textNode using txt() ###
            if typeof children is "string"
                @element.inject(txt(children))
            else
                ### If children is an array of elems, iterate and add ###
                if isArray children
                    for child in children
                        ### String? Convert via txt() then ###
                        if typeof child is "string"
                            @element.inject(txt(child))
                        else
                            ### Plain element, add normally ###
                            @element.inject(child)
                else
                    ### Just a single element, add it ###
                    @element.inject(children)
        return @element
###*
# prototype injector for HTML elements:
# Example: mydiv.inject(otherdiv)
###
HTMLElement.prototype.inject = (child) ->
    if isArray(child)
        for item in child
            # Convert to textNode if string
            if typeof item is 'string'
                item = txt(item)
            this.appendChild(item)
    else
        # Convert to textNode if string
        if typeof child is 'string'
            child = txt(child)
        this.appendChild(child)
    return child
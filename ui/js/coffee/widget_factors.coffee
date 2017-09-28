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


factors = (json, state) ->
    items = []
    if json.factors
        id = parseInt(Math.random()*99999999).toString(16)
        obj = new HTML('div', { id: id})
        for factor in json.factors
            h = new HTML('h1', {}, txt(factor.count.pretty()))
            if factor.previous
                direction = factor.count - factor.previous
                pct = parseInt((direction/factor.previous)* 100)
                if direction < 0
                    h2 = new HTML('span', { style: { marginLeft: "8px", fontSize: "14px", color: 'red'}},[
                        new HTML('i', {class: "fa fa-chevron-circle-down"}),
                        " #{pct}% change since last period"
                    ])
                    h.inject(h2)
                else 
                    h2 = new HTML('span', { style: { marginLeft: "8px", fontSize: "14px", color: 'green'}},[
                        new HTML('i', {class: "fa fa-chevron-circle-up"}),
                        " +#{pct}% change since last period"
                    ])
                    h.inject(h2)
                        
            t = txt(factor.title)
            obj.inject(new HTML('div', {}, [h,t]))
        state.widget.inject(obj, true)
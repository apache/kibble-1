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

make5 = (obj, json, pos) ->
    what = json.topN.denoter
    for item, i in json.topN.items[pos...pos+5]
        if i == 5
            break
        idiv = new HTML('div', { class: "media event"} )
        left = new HTML('a', { class: "pull-left"})
        if item.gravatar
            left.inject(new HTML('img', { class: "img-circle img-reponsive", src: "https://secure.gravatar.com/avatar/#{item.gravatar}.png?d=identicon" ,style: { width: "32px", height: "32px"}}))
        else if json.topN.icon
            left.inject(new HTML('i', { class: "fa fa-#{json.topN.icon}", style: { fontSize: "28px"}}))
        right = new HTML('div', { class: "media event"})
        rightInner = new HTML('div', { class: "media-body"})
        right.inject(rightInner)
        if item.email
            title = new HTML('a', { class: "title", href:"contributors.html?page=biography&email=#{item.email}"}, txt(item.name))
            rightInner.inject(title)
            rightInner.inject(" - ")
            filter = new HTML('a', { class: "title", href:"javascript: void(filterPerson('#{item.email}'));"}, "[filter]")
            rightInner.inject(filter)
        else if item.url
            if item.title
                item.tooltip = item.title
                if item.title.length > 40
                    item.title = item.title.toString().substring(0,40) + "..."
                item.name += ": " + item.title
            # Sometimes, scanners add a spurious extra slash. nix it.
            item.url = item.url.replace(/([^:])(\/\/+)/g, '$1/')
            title = new HTML('a', { title: item.tooltip, class: "title", href:item.url}, txt(item.name))
            rightInner.inject(title)
        else
            title = new HTML('a', { class: "title"}, txt(item.name))
            rightInner.inject(title)
        fodder = new HTML('p', {})
        fodder.inject(new HTML('b', {}, item.count.pretty()))
        fodder.inject(txt(" #{what} during this period"))
        if item.subcount
            fodder.inject(new HTML('br'))
            t = []
            for k,v of item.subcount
                t.push(v.pretty() + " " + k)
            fodder.inject(new HTML('small', {}, (t.join(", ") + ".")))
        rightInner.inject(fodder)
        idiv.inject(left)
        idiv.inject(right)
        obj.inject(idiv)

top5 = (json, state) ->
    items = []
    if json.topN
        id = parseInt(Math.random()*99999999).toString(16)
        obj = new HTML('div', { id: id})
        make5(obj, json, 0)
        state.widget.inject(obj, true)
        pos = 5
        while pos < json.topN.items.length
            nid = id + "_show_" + pos
            
            obj.inject(new HTML('a', { style: { cursor: 'pointer'}, onclick: "this.style.display = 'none'; get('#{nid}').style.display = 'block';"}, "Show more..."))
            obj = new HTML('div', { id: nid, style: { display: 'none'}})
            make5(obj, json, pos)
            state.widget.inject(obj)
            pos += 5
        

         
showMore = (id) ->
    obj = document.getElementById(id)
    if obj
        obj.style.display = "block"
            

filterPerson = (email) ->
    if email == ""
        email = null
    updateWidgets('donut', null, { email: email })
    updateWidgets('line', null, { email: email })
    updateWidgets('contacts', null, { email: email })
    updateWidgets('top5', null, { email: email })
    updateWidgets('trends', null, { email: email })
    updateWidgets('relationship', null, { email: email })
    updateWidgets('viewpicker', null, { email: email })
    globArgs.email = email
              
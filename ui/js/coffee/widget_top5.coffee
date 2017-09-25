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

top5 = (json, state) ->
        people = []
        if state.widget.args.source == 'mail-subjects'
            obj = document.createElement('div')
            i = 0
            for item in json.top
                i++
                if i > 5
                    break
                p = ""
                obj.innerHTML += '<div class="media event">                            <a class="pull-left">   <i class="fa fa-envelope" style="font-size: 32pt;"></i></a>                            <div class="media-body">                              <a class="title" href="#" >'+item[0]+'</a>                              <p><strong>'+item[1].pretty()+'</strong> interactions' + p + '.</p>'
            state.widget.inject(obj, true)
            if json.top.length > 5
                id = Math.floor(Math.random()*987654321).toString(16)
                obj.innerHTML += "<p><a href='javascript:void(0);' onclick='this.style.display=\"none\"; showMore(\""+id+"\");'>Show more</a></p>"
                obj2 = document.createElement('div')
                obj2.setAttribute("id", id)
                obj2.style.display = "none"
                for i in [5..9]
                    item = json.top[i]
                    if i
                        obj2.innerHTML += '<div class="media event">                            <a class="pull-left">   <i class="fa fa-envelope" style="font-size: 32pt;"></i></a>                            <div class="media-body">                              <a class="title" href="#" >'+item[0]+'</a>                              <p><strong>'+item[1].pretty()+'</strong> interactions' + p + '.</p>'
                state.widget.inject(obj2)
        else if state.widget.args.source == 'issue-top'
            obj = document.createElement('div')
            if json.title
                obj.innerHTML += "<h2>" + json.title + "</h2>"
            i = 0
            for item in json.top
                i++
                if i > 5
                    break
                p = ""
                obj.innerHTML += '<div class="media event">                            <a class="pull-left"> <i class="fa fa-wpforms" style="font-size: 32pt;"></i> </a>                            <div class="media-body">                              <a class="title" href="'+item.source+'" target="_blank" >'+item.key+'</a>: ' + item.title + '<p><strong>'+item.comments.pretty()+'</strong> interactions' + p + '.</p>'
            state.widget.inject(obj, true)
            if json.top.length > 5
                id = Math.floor(Math.random()*987654321).toString(16)
                obj.innerHTML += "<p><a href='javascript:void(0);' onclick='this.style.display=\"none\"; showMore(\""+id+"\");'>Show more</a></p>"
                obj2 = document.createElement('div')
                obj2.setAttribute("id", id)
                obj2.style.display = "none"
                for i in [5..9]
                    item = json.top[i]
                    if i
                        obj2.innerHTML += '<div class="media event">                            <a class="pull-left"> <i class="fa fa-wpforms" style="font-size: 32pt;"></i> </a>                            <div class="media-body">                              <a class="title" href="'+item.source+'" target="_blank" >'+item.key+'</a>: ' + item.title + '<p><strong>'+item.comments.pretty()+'</strong> interactions' + p + '.</p>'
                state.widget.inject(obj2)
        else
            if state.widget.args.source == 'committers' or (json.widget and json.widget.match(/commit/))
                    for person, data of json.people
                            people.push([person, data.changes])
                    people.sort((a,b) => b[1].commits - a[1].commits)
            obj = document.createElement('div')
            if json.title
                obj.innerHTML += "<h2>" + json.title + "</h2>"
            p = "during this period"
            if state.widget.args.daterangeRaw
                    from = new Date(state.widget.args.daterangeRaw[0]*1000).toDateString()
                    to = new Date(state.widget.args.daterangeRaw[1]*1000).toDateString()
                    p = "between " + from + " and " + to
            if state.widget.args.source == 'mail-authors'                
                    for person, data of json.individuals
                            people.push([person, data])
                    people.sort((a,b) => b[1].emails - a[1].emails)
            if state.widget.args.source == 'issue-closers'                
                    for person, data of json.individuals
                            people.push([person, data])
                    people.sort((a,b) => b[1].closed - a[1].closed)
            if state.widget.args.source == 'issue-creators'                
                    for person, data of json.individuals
                            people.push([person, data])
                    people.sort((a,b) => b[1].created - a[1].created)
            if state.widget.args.source == 'im-authors'                
                    for person, data of json.individuals
                            people.push([person, data])
                    people.sort((a,b) => b[1].messages - a[1].messages)
            p = "during this period"
            if state.widget.args.daterangeRaw
                    from = new Date(state.widget.args.daterangeRaw[0]*1000).toDateString()
                    to = new Date(state.widget.args.daterangeRaw[1]*1000).toDateString()
                    p = "between " + from + " and " + to
            for i in [0..4]
                    if people[i]
                            committer = json.people[people[i][0]]
                            if committer
                                committer.count = people[i][1].commits
                                committer.name = committer.name.replace(/\\/g, '')
                                if committer.email != 'invalid@invalid' and not json.widget
                                    committer.name += " <a style='font-size: 8pt;' href='javascript:void(0);' onclick='filterPerson(\"" + committer.email + "\");'>[filter]</a>"
                                changes = ""
                                if people[i][1].insertions or people[i][1].deletions
                                        changes = (people[i][1].insertions + people[i][1].deletions).pretty() + " lines changed (" + people[i][1].insertions.pretty() + " insertions, " + people[i][1].deletions.pretty() + " deletions)."
                                        plink = '?page=people&email='+people[i][0]
                                        if json.widget
                                            plink = '#'
                                        obj.innerHTML += '<div class="media event" style="line-height: 14px;">                            <a class="pull-left">   <img style="width: 48px; height: 48px;" class="img-circle img-responsive" src="https://secure.gravatar.com/avatar/' + committer.md5 + '.png?d=identicon"/>                         </a>                            <div class="media-body">                              <a class="title" href="'+plink+'" >'+committer.name+'</a>                              <p><strong>'+people[i][1].commits.pretty()+'</strong> commits ' + p + '.<br/><small>' + changes + '</small>                              </p>                            </div>                          </div>'
                                if people[i][1].emails
                                    changes = (people[i][1].emails).pretty() + " emails sent."
                                    plink = '?page=people&email='+people[i][0]
                                    if json.widget
                                        plink = '#'
                                    obj.innerHTML += '<div class="media event">                            <a class="pull-left">   <img style="width: 48px; height: 48px;" class="img-circle img-responsive" src="https://secure.gravatar.com/avatar/' + committer.md5 + '.png?d=identicon"/>                         </a>                            <div class="media-body">                              <a class="title" href="'+plink+'" >'+committer.name+'</a>                              <p><strong>'+people[i][1].emails.pretty()+'</strong> emails ' + p + '.</p>'
                                if people[i][1].messages
                                    changes = (people[i][1].messages).pretty() + " messages sent."
                                    obj.innerHTML += '<div class="media event">                            <a class="pull-left">   <img style="width: 48px; height: 48px;" class="img-circle img-responsive" src="https://secure.gravatar.com/avatar/' + committer.md5 + '.png?d=identicon"/>                         </a>                            <div class="media-body">                              <b>'+committer.name+'</b>                              <p><strong>'+people[i][1].messages.pretty()+'</strong> messages ' + p + '.</p>'
                                if people[i][1].closed
                                    changes = (people[i][1].closed).pretty() + " issues closed."
                                    obj.innerHTML += '<div class="media event">                            <a class="pull-left">   <img style="width: 48px; height: 48px;" class="img-circle img-responsive" src="https://secure.gravatar.com/avatar/' + committer.md5 + '.png?d=identicon"/>                         </a>                            <div class="media-body">                              <a class="title" href="?page=people&email='+people[i][0]+'" >'+committer.name+'</a>                              <p><strong>'+people[i][1].closed.pretty()+'</strong> issues closed ' + p + '.</p>'
                                if people[i][1].created
                                    changes = (people[i][1].created).pretty() + " issues created."
                                    obj.innerHTML += '<div class="media event">                            <a class="pull-left">   <img style="width: 48px; height: 48px;" class="img-circle img-responsive" src="https://secure.gravatar.com/avatar/' + committer.md5 + '.png?d=identicon"/>                         </a>                            <div class="media-body">                              <a class="title" href="?page=people&email='+people[i][0]+'" >'+committer.name+'</a>                              <p><strong>'+people[i][1].created.pretty()+'</strong> issues created ' + p + '.</p>'
            state.widget.inject(obj, true)
            if people.length > 5 and not json.widget
                id = Math.floor(Math.random()*987654321).toString(16)
                obj.innerHTML += "<p><a href='javascript:void(0);' onclick='this.style.display=\"none\"; showMore(\""+id+"\");'>Show more</a></p>"
                obj2 = document.createElement('div')
                obj2.setAttribute("id", id)
                obj2.style.display = "none"
                for i in [5..9]
                        if people[i]
                                committer = json.people[people[i][0]]
                                if committer
                                    committer.count = people[i][1].commits
                                    committer.name = committer.name.replace(/\\/g, '')
                                    committer.name += " [<a href='javascript:void(0);' onclick='filterPerson(\"" + committer.email + "\");'>filter</a>]"
                                    changes = ""
                                    if people[i][1].insertions or people[i][1].deletions
                                            changes = (people[i][1].insertions + people[i][1].deletions).pretty() + " lines changed (" + people[i][1].insertions.pretty() + " insertions, " + people[i][1].deletions.pretty() + " deletions)."
                                            obj2.innerHTML += '<div class="media event">                            <a class="pull-left">   <img style="width: 48px; height: 48px;" class="img-circle img-responsive" src="https://secure.gravatar.com/avatar/' + committer.md5 + '.png?d=identicon"/>                         </a>                            <div class="media-body">                              <a class="title" href="?page=people&email='+people[i][0]+'" >'+committer.name+'</a>                              <p><strong>'+people[i][1].commits.pretty()+'</strong> commits ' + p + '.</p>                              <p> <small>' + changes + '</small>                              </p>                            </div>                          </div>'
                                    if people[i][1].emails
                                        changes = (people[i][1].emails).pretty() + " emails sent."
                                        obj2.innerHTML += '<div class="media event">                            <a class="pull-left">   <img style="width: 48px; height: 48px;" class="img-circle img-responsive" src="https://secure.gravatar.com/avatar/' + committer.md5 + '.png?d=identicon"/>                         </a>                            <div class="media-body">                              <a class="title" href="?page=people&email='+people[i][0]+'" >'+committer.name+'</a>                              <p><strong>'+people[i][1].emails.pretty()+'</strong> emails ' + p + '.</p>'
                                    if people[i][1].closed
                                        changes = (people[i][1].closed).pretty() + " issues closed."
                                        obj2.innerHTML += '<div class="media event">                            <a class="pull-left">   <img style="width: 48px; height: 48px;" class="img-circle img-responsive" src="https://secure.gravatar.com/avatar/' + committer.md5 + '.png?d=identicon"/>                         </a>                            <div class="media-body">                              <a class="title" href="?page=people&email='+people[i][0]+'" >'+committer.name+'</a>                              <p><strong>'+people[i][1].closed.pretty()+'</strong> issues closed ' + p + '.</p>'
                                    if people[i][1].created
                                        changes = (people[i][1].created).pretty() + " issues created."
                                        obj2.innerHTML += '<div class="media event">                            <a class="pull-left">   <img style="width: 48px; height: 48px;" class="img-circle img-responsive" src="https://secure.gravatar.com/avatar/' + committer.md5 + '.png?d=identicon"/>                         </a>                            <div class="media-body">                              <a class="title" href="?page=people&email='+people[i][0]+'" >'+committer.name+'</a>                              <p><strong>'+people[i][1].created.pretty()+'</strong> issues created ' + p + '.</p>'
                                    if people[i][1].messages
                                        changes = (people[i][1].messages).pretty() + " messages sent."
                                        obj2.innerHTML += '<div class="media event">                            <a class="pull-left">   <img style="width: 48px; height: 48px;" class="img-circle img-responsive" src="https://secure.gravatar.com/avatar/' + committer.md5 + '.png?d=identicon"/>                         </a>                            <div class="media-body">                              <b>'+committer.name+'</b>                              <p><strong>'+people[i][1].messages.pretty()+'</strong> messages ' + p + '.</p>'
                state.widget.inject(obj2)              
            if people.length == 0
                    obj.innerHTML = "No data found for this period."
         
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
    globArgs.email = email
              
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

keyValueForm = (type, key, caption, placeholder) ->
    div = new HTML('div', { style: { width: "100%", margin: "10px", paddingBottom: "10px"}})
    left = new HTML('div', { style: { float: "left", width: "300px", fontWeight: "bold"}}, caption)
    right = new HTML('div', { style: { float: "left", width: "500px"}}) 
    
    if type == 'text'
        inp = new HTML('input', {name: key, id: key, style: { marginBottom: "10px"}, class: "form-control", type: "text", placeholder: placeholder})
        right.inject(inp)
    if type == 'textarea'
        inp = new HTML('textarea', {name: key, id: key, style: { marginBottom: "10px"}, class: "form-control", placeholder: placeholder})
        right.inject(inp)
    div.inject([left, right])
    return div

orgCreated = (json, state) ->
    if json.okay
        location.reload()

setDefaultOrg = (orgid) ->
    patch('account', { email: userAccount.email, defaultOrganisation: orgid}, {}, defaultOrgChanged)

defaultOrgChanged = (json, state) ->
    window.setTimeout(
        () ->
            location.reload()
        , 1000)

makeOrg = () ->
    orgname = get('orgname').value
    orgdesc = get('orgdesc').value
    orgid = get('orgid').value
    if orgid.length == 0
        orgid = parseInt(Math.random()*987654321).toString(16)
    if orgname.length  == 0
        alert("Please enter a name for the organisation!")
        return
    if orgdesc.length  == 0
        alert("Please enter a description of the organisation!")
        return
    put('org/list', {id: orgid, name: orgname, desc: orgdesc}, {}, orgCreated)


orglist = (json, state) ->
    items = []
    if json.organisations.length == 0
        obj = new HTML('div')
        obj.inject(new HTML('h3', {}, "You don't seem to belong to any organisations just yet."))
        if userAccount.userlevel == 'admin'
            obj.inject("...but you can make one!")
        state.widget.inject(obj, true)
    else
        odiv = new HTML('div')
        for org in json.organisations
            isDefault = (org.id == userAccount.defaultOrganisation)
            div = new HTML('div', { class: "orgItem " + (if isDefault then "orgSelected" else "")})
            div.inject(new HTML('h1', {}, org.name + (if isDefault then " (Current)" else "")))
            div.inject(new HTML('p', {}, org.description or ""))
            div.inject([
                new HTML('kbd', {}, ""+org.docCount.pretty()),
                " objects collected from ",
                new HTML('kbd', {}, ""+org.sourceCount.pretty()),
                " sources so far."
                ])
            
            odiv.inject(div)
            if not isDefault
                dbtn = new HTML('input', { style: { marginTop: "10px", width: "120px"},class: "btn btn-primary btn-block", type: "button", onclick: "setDefaultOrg('#{org.id}');", value: "Set as current"})
                div.inject(dbtn)
            odiv.inject(new HTML('hr'))
        state.widget.inject(odiv, true)
        
    if userAccount.userlevel == "admin"
        fieldset = new HTML('fieldset', { style: { float: "left", margin: '30px'}})
        legend = new HTML('legend', {}, "Create a new organisation:")
        fieldset.inject(legend)
        
        fieldset.inject(keyValueForm('text', 'orgname', 'Name of the organisation:', 'Foo, inc.'))
        fieldset.inject(keyValueForm('textarea', 'orgdesc', 'Description:', 'Foo, inc. is awesome and does stuff.'))
        fieldset.inject(keyValueForm('text', 'orgid', 'Optional org ID:', 'demo, myorg etc'))
        
        fieldset.inject(new HTML('p', {}, "You'll be able to add users and owners once the organisation has been created."))
        
        btn = new HTML('input', { style: { width: "200px"},class: "btn btn-primary btn-block", type: "button", onclick: "makeOrg();", value: "Create organisation"})
        fieldset.inject(btn)
        
        state.widget.inject(fieldset)
        

inviteMember = (eml, admin) ->
    put('org/members', { email: eml, admin: admin}, null, memberInvited)
    
removeMember = (eml, admin) ->
    xdelete('org/members', { email: eml, admin: admin}, null, memberInvited)

memberInvited = (json, state) ->
    window.setTimeout(
        () ->
            location.reload()
        , 1000
        )

membershipList = (json, state) ->
    
    # Invite member form
    h = new HTML('h3', {}, "Invite a member to #{userAccount.defaultOrganisation}")
    state.widget.inject(h, true)
    inp = new HTML('input', {id: "email", type: "text", placeholder: "email@ddres"})
    btn = new HTML('input', {type: 'button', class: 'btn btn-success', value: "Invite member", onclick: 'inviteMember(get("email").value, false);'})
    state.widget.inject(inp)
    state.widget.inject(btn)
    state.widget.inject(new HTML('hr'))
    
    
    # Existing membership list
    h = new HTML('h3', {}, "Current membership of #{userAccount.defaultOrganisation}:")
    state.widget.inject(h)
    list = new HTML('table', { style: { margin: "20px", border: "1px solid #666"}})
    
    for member in json.members
        tr = new HTML('tr', { style: { borderBottom: "1px solid #666"}})
        eml = new HTML('td', { style: { padding: "5px"}}, member)
        isAdmin = member in json.admins
        admin = new HTML('td', { style: { padding: "5px"}}, if isAdmin then "Admin" else "Member")
        alink = new HTML('a', { href: "javascript:void(inviteMember('#{member}', true));"}, "Make admin")
        if isAdmin
            alink = new HTML('a', { href: "javascript:void(inviteMember('#{member}', false));"}, "Remove as admin")
        admopt = new HTML('td', { style: { padding: "5px"}}, alink)
        
        # Remove member
        dlink = new HTML('a', { href: "javascript:void(removeMember('#{member}'));"}, "Remove from organisation")
        delopt = new HTML('td', { style: { padding: "5px"}}, dlink)
        
        tr.inject(eml)
        tr.inject(admin)
        tr.inject(admopt)
        tr.inject(delopt)
        list.inject(tr)
        
    state.widget.inject(list)
    


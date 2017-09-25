phonebook_cached = {}

fetchPhonebook = (args) ->
        if (args) 
            wargs = JSON.stringify(args)
            if (phonebook_cached[wargs])
                renderPhonebook(phonebook_cached[wargs], args)
                return
                
        args.widget.cog()
        url = "people/"
        
        postJSON(url, args, args, renderPhonebook)

setupPhonebook = (widget, w) ->
        fetchPhonebook({ widget: widget, w: w, letter: 'a', project:  w.target or "" })


renderPhonebook = (json, state) ->
        wargs = JSON.stringify(state)
        phonebook_cached[wargs] = json
        letters = "abcdefghijklmnopqrstuvwxyz".split("")
        row = document.createElement('div')
        row.setAttribute("class", "row")
        rdiv = document.createElement('div')
        rdiv.setAttribute("class", "col-md-12 col-sm-12 col-xs-12 text-center")
        ul = document.createElement('ul')
        ul.setAttribute("class", "pagination pagination-split")
        for letter in letters
                li = document.createElement('li')
                a = document.createElement('a')
                a.setAttribute("href", "#")
                a.addEventListener("click", () ->
                        state.letter = this.childNodes[0].data.toLowerCase()
                        fetchPhonebook(state)
                , false)
                a.appendChild(document.createTextNode(letter.toUpperCase()))
                if (state.letter && letter == state.letter)
                    li.setAttribute("class", "active")
                
                li.appendChild(a)
                ul.appendChild(li)

        rdiv.appendChild(ul)
        row.appendChild(rdiv)
        
        state.widget.inject(row, true)
        
        
        # Render entries
        row = mk('table', {class:"display"}, mk('thead', {}, mk('tr', {}, [mk('th', {}, 'Avatar'), mk('th', {}, 'Name'), mk('th', {}, 'Email')])))
        
        people = []
        json.people.sort( (a,b) => if (a.name == b.name) then 0 else (if a.name > b.name then 1 else -1))
        a = 0
        for person in json.people
            a++
            imgsrc = document.createElement('img')
            imgsrc.setAttribute("class", "img-circle img-responsive")
            imgsrc.setAttribute("onshow", "this.src = 'https://secure.gravatar.com/avatar/" + person.md5 + ".png?d=identicon'")
            people.push(["https://secure.gravatar.com/avatar/" + person.md5 + ".png?d=identicon", person.name, person.email])
            
        state.widget.inject(row)
        tbl = $(row).DataTable(
            serverSide: true,
            searching: false,
            lengthMenu: [[25, 50, 100], [25, 50, 100]]
            columnDefs: [ {
                targets: 0,
                data: "avatar",
                render: ( data, type, full, meta ) ->
                  return '<img class="img-circle img-responsive" style="width: 24px; height: 24px;" src="'+full[0]+'"/>';
            },
             {
                targets: 1,
                data: "email",
                render: ( data, type, full, meta ) ->
                  return '<a href="?page=people&email='+full[2]+'">' + full[1] + "</a>"
            }]
            ajax: ( data, callback, settings ) ->
                out = [];
                for i in [data.start...(data.start+data.length)]
                    out.push(people[i])
    
                setTimeout( () ->
                    callback( {
                        draw: data.draw,
                        data: out,
                        recordsTotal: people.length,
                        recordsFiltered: people.length
                    })
                , 50 )
        scrollY: 200,
        scroller: {
            loadingIndicator: true
        })
        
        
        ###
            card = document.createElement('div')
            card.setAttribute("class", "col-md-3 col-sm-4 col-xs-12 profile_details")
            well = document.createElement('div')
            well.setAttribute("class", "well profile_view")
            well.style.width = "100%"
            card.appendChild(well)
            
            namecard = document.createElement('div')
            namecard.setAttribute("class", "left col-xs-7")
            img = document.createElement('div')
            img.setAttribute("class", "right col-xs-5 text-center")
            imgsrc = document.createElement('img')
            imgsrc.setAttribute("class", "img-circle img-responsive")
            imgsrc.setAttribute("src", "https://secure.gravatar.com/avatar/" + person.md5 + ".png?d=identicon")
            img.appendChild(imgsrc)
            well.appendChild(namecard)
            well.appendChild(img)
            a = document.createElement('a')
            a.setAttribute('href', '?page=people&email=' + person.email)
            name = document.createElement('h2')
            name.appendChild(document.createTextNode(person.name))
            a.appendChild(name)
            namecard.appendChild(a)
            namecard.appendChild(document.createTextNode(person.email))
            groups = []
            if person.tags
                for tag in person.tags
                    if tag != '_untagged'
                        groups.push(tag)
            if groups.length > 0
                namecard.appendChild(mk('br'))
                namecard.appendChild(txt("Part of: " + groups.join(", ")))
            
            row.appendChild(card)
        ###
            
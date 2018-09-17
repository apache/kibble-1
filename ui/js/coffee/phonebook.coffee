
phonebook = (json, state) ->
    items = []
    if json.people
        id = parseInt(Math.random()*99999999).toString(16)
        obj = new HTML('div', { id: id})
        obj.innerText = "Found #{json.people.length} contributors.."
        obj.inject(new HTML('br'))
        state.widget.inject(obj, true)
        
        json.people.sort( (a,b) =>
                if a.name < b.name
                        return -1
                if a.name > b.name
                        return 1
                return 0
        )
        
        for i, item of json.people
                if i > 250
                        break
                idiv = new HTML('div', { class: "phonebook_entry"} )
                left = new HTML('a', { class: "pull-left"})
                if item.gravatar
                    left.inject(new HTML('img', { class: "img-circle img-reponsive", src: "https://secure.gravatar.com/avatar/#{item.gravatar}.png?d=identicon" ,style: { width: "32px", height: "32px"}}))
                right = new HTML('div', { class: "media event"})
                rightInner = new HTML('div', { style: {marginLeft: '10px', width: '280px', height: '24px', display: 'inline-block', overflow: 'hidden', textOverflow: 'ellipsis'}})
                right.inject(rightInner)
                if item.email
                    title = new HTML('a', { class: "title", href:"contributors.html?page=biography&email=#{item.email}"}, txt(item.name))
                    rightInner.inject(title)
                    rightInner.inject(' - ' + item.contributions + ' contribution' + (if item.contributions != 1 then 's' else ''))
                idiv.inject(left)
                idiv.inject(right)
                obj.inject(idiv)
                

        
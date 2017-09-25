messages = (json, state) ->
    
    if isArray json
        obj = document.createElement('form')

        tbl = mk('table')
        set(tbl, 'class', 'table table-striped')
        thead = mk('thead')
        tr = mk('tr')
        for el in ['Date', 'Sender', 'Subject']
            td = mk('th')
            if el.match(/(Date|Sender)/)
                td.style.width = "20%"
            app(td, txt(el))
            app(tr, td)
        app(thead, tr)
        app(tbl, thead)
        
        tbody = mk('tbody')
        app(tbl, tbody)
        
        for message in json
            tr = mk('tr')
            if message.read == false
                tr.style.fontWeight = "bold"
                tr.style.color = "#396"
            td = mk('td')
            a = mk('a')
            set(a, 'href', '?page=messages&message=' + message.id)
            app(a, txt(new Date(message.epoch*1000).toString()))
            app(td, a)
            app(tr, td)
            
            td = mk('td')
            a = mk('a')
            set(a, 'href', '?page=messages&message=' + message.id)
            app(a, txt(message.senderName))
            app(td, a)
            app(tr, td)
            
            td = mk('td')
            a = mk('a')
            set(a, 'href', '?page=messages&message=' + message.id)
            app(a, txt(message.subject))
            app(td, a)
            app(tr, td)
            app(tbody, tr)
            
        app(obj, tbl)
        
        items =
            recipient: 'Recipient ID'
            subject: "Message subject"
            body: "Message"
            
        h2 = mk('h2')
        app(h2, txt("Send a message:"))
        app(obj, h2)
        
        for item in ['recipient', 'subject', 'body']
            div = mk('div')
            app(div, txt(items[item] + ": "))
            if item == 'body'
                inp = mk('textarea')
                inp.style.width = "600px"
                inp.style.height = "200px"
            else
                inp = mk('input')
                set(inp, 'type', 'text')
                inp.style.width = "200px"
            set(inp, 'name', item)
            app(div, inp)
            app(obj, div)
        
        btn = mk('input')
        set(btn, 'type', 'button')
        set(btn, 'onclick', 'sendEmail(this.form)')
        set(btn, 'value', "Send message")
        app(obj, btn)
        
        #obj.innerHTML += JSON.stringify(json)
        state.widget.inject(obj, true)
    else
        obj = mk('div')
        b = mk('b')
        app(b, txt("Sender: "))
        app(obj, b)
        app(obj, txt(json.senderName + ' (' + json.sender + ')'))
        app(obj, mk('br'))
        
        b = mk('b')
        app(b, txt("Date: "))
        app(obj, b)
        app(obj, txt(new Date(json.epoch*1000).toString()))
        app(obj, mk('br'))
        
        b = mk('b')
        app(b, txt("Subject: "))
        app(obj, b)
        app(obj, txt(json.subject))
        app(obj, mk('br'))
        app(obj, mk('br'))
        
        pre = mk('pre')
        app(pre, txt(json.body))
        app(obj, pre)
        
        app(obj, mk('hr'))
        
        form = mk('form')
        items =
            recipient: 'Recipient ID'
            subject: "Message subject"
            body: "Message"
            
        h2 = mk('h2')
        app(h2, txt("Send a reply:"))
        app(form, h2)
        
        reply = {
            recipient: json.sender
            subject: 'RE: ' + json.subject
            body: ''
        }
        
        for item in ['recipient', 'subject', 'body']
            div = mk('div')
            app(div, txt(items[item] + ": "))
            if item == 'body'
                inp = mk('textarea')
                inp.style.width = "600px"
                inp.style.height = "200px"
            else
                inp = mk('input')
                set(inp, 'type', 'text')
                inp.style.width = "200px"
            inp.value = reply[item]
            set(inp, 'name', item)
            app(div, inp)
            app(form, div)
        
        btn = mk('input')
        set(btn, 'type', 'button')
        set(btn, 'onclick', 'sendEmail(this.form)')
        set(btn, 'value', "Send message")
        app(form, btn)
        
        app(obj, form)
        state.widget.inject(obj, true)

sendEmail = (form) ->
    js = {
        action: 'send'
    }
    for i in [0..form.length-1]
        k = form[i].name
        v = form[i].value
        if k in ['recipient', 'subject', 'body']
            js[k] = v
    postJSON("messages", js, null, (a) -> alert("Mail sent!") )
        
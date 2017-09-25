# Paragraph widget
paragraph = (json, state) ->
    lmain = mk('div')
    state.widget.parent.inject(lmain, true)
    if json.title
      title = mk('h1', {}, json.title)
      app(lmain, title)
    if json.text
      if isArray(json.text)
        for p in json.text
          para = mk('p', {style:"font-size: 1.2rem;"}, p)
          app(lmain, para)
      else
          app(lmain, mk('p', {style:"font-size: 1.2rem;"}, json.text))


    
viewJS = {}
publisherWidget = null

publisherPublic = (json, state) ->
    publisher(json, state, true)
    
publisher = (json, state, nolink) ->
        div = document.createElement('div')
        state.public = true
        twidget = json.widget.replace(/(-\d?year|-all|-month)/, "")
        if twidget in ['repo-relationship', 'issue-relationship', 'mail-relationship']
            relationship(json, state)
        if twidget in ['languages', 'compare-commits', 'repo-size', 'repo-commits']
            donut(json, state)
        else if twidget in ['evolution', 'evolution-extended', 'commit-history', 'committer-count', 'issue-count','issue-operators', 'commit-lines', 'email-count', 'issue-queue', 'file-age', 'file-creation', 'im-stats', 'log-stats']
            linechart(json, state)
        else if twidget in ['log-map']
            worldmap(json, state)
        else if twidget in ['sloc-map']
            treemap(json, state)
        else if twidget.match(/top/)
            top5(json, state)
        viewJS = JSON.stringify({
            view: json.eview,
            widget: json.widget
        }
        )
        if not nolink
            link = mk('input', { type: "button", class:"btn btn-success", value: "Publish this widget", onclick: "publishWidget();"})
            state.widget.inject(link)
            publisherWidget = state.widget
        else
            if not location.href.match(/snoot\.io/)
                link = mk('a', { href: "https://www.snoot.io/", style: "font-size: 10px; margin-left: 60px; font-family: sans-serif;"}, "Data courtesy of Snoot.io")
                state.widget.inject(link)
        
publishWidget = () ->
    postJSON("publish", {
        publish: JSON.parse(viewJS)
    }, null, postPublishLink)
    
postPublishLink = (json, state) ->
    if json.id
        pdiv = get('publishercode')
        if not pdiv
            pdiv = mk('pre', {id:"publishercode", style: "padding: 5px; border: 1px dashed #333; background: #FFD;"})
            publisherWidget.inject(pdiv)
        pdiv.innerHTML = ""
        added = ""
        if json.type and json.type.match(/log-map/)
            added = "\n<script src=\"https://www.snoot.io/js/worldmap.js\"></script>\n"
        app(pdiv, txt("Script code for publishing:\n\n<div class=\"snoot-widget\" data=\"" + json.id + "\"></div>\n<script src=\"https://www.snoot.io/js/snoot.all.3.js\"></script>\n<script src=\"https://www.snoot.io/publish/bundle.js\"></script>#{added}"))
    else
        alert("Something broke :(")
    
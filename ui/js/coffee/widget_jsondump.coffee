jsondump = (json, state) ->
    pre = new HTML('pre', { style: { whiteSpace: 'pre-wrap'}})
    pre.inject(JSON.stringify(json, null, 2))
    state.widget.inject(pre, true)


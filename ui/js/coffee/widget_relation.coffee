relationship = (json, state) ->
        div = document.createElement('div')
        state.widget.inject(div, true)
        chart = new Chart(div, 'relationship', json, {})
        
        

badModal = (str) ->
    modalBox = new HTML('div', { class: "errorModal"})
    document.body.appendChild(modalBox)
    modalInner = new HTML('div', { class: "errorModalInner" }, str)
    modalBox.appendChild(modalInner)
    btndiv = new HTML('div', {style: {textAlign: "center", marginTop: "10px"}}, " ")
    modalInner.inject(btndiv)
    btn = new HTML('button', {class: "btn btn-lg btn-success", onclick:"document.body.removeChild(this.parentNode.parentNode.parentNode);"}, "Gotcha!")
    btndiv.inject(btn)
    
    window.setTimeout(() ->
            modalInner.style.visibility = "visible"
            modalInner.style.opacity = 1
        , 10
        )


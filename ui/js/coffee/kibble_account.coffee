kibbleLoginCallback = (json, state) ->
    # Everything okay, redirect to dashboard :)
    location.href = "dashboard.html"

kibbleLogin = (email, password) ->
    put("session", {email: email, password: password}, null, kibbleLoginCallback)
    return false

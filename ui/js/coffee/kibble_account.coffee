kibbleLoginCallback = (json, state) ->
    userAccount = json
    # Everything okay, redirect to dashboard :)
    m = location.href.match(/\?redirect=(.+)$/)
    if m and not m[1].match(/:/)
        location.href = m[1]
    else
        location.href = "organisations.html?page=org"

kibbleLogin = (email, password) ->
    put("session", {email: email, password: password}, null, kibbleLoginCallback)
    return false

signout = () ->
    xdelete('session', {}, {}, () -> location.href = 'login.html')
    
signup = (form) ->
    err = null
    if form.name.value.length < 2
        err = "Please enter your full name"
    else if form.screenname.value.length < 1
        err = "Please enter a screen name"
    else if form.email.value.length < 6 or not form.email.value.match(/^[^\r\n\s @]+@[^\r\n\s @]+$/)
        err = "Please enter a valid email address"
    else if form.password.value.length < 1 or form.password.value != form.password2.value
        err = "Please enter your password and make sure it matches the re-type"
    if err
        document.getElementById('signupmsg').innerHTML = "<h2>Error: " + err + "</h2>"
        return false
    else
        document.getElementById('signupmsg').innerHTML = "Creating account, hang on..!"
        post('user-signup',
             {
                action: 'create',
                name: form.name.value,
                password: form.password.value,
                screenname: form.screenname.value,
                email: form.email.value,
                code: form.code.value
                }
            , null, validateSignup)
        return false

validateSignup = (json, state) ->
    if json.created
        document.getElementById('signupmsg').innerHTML = "<span style='color: #060;'>Account created! Please check your inbox for verification instructions.</span>"
    else
        document.getElementById('signupmsg').innerHTML = "<h2 style='font-size: 2rem; color: #830;'>Error: " + json.message + "</h2>"
        
login = (form) ->
    if form.email.value.length > 5 and form.password.value.length > 0
        cog(document.getElementById('loginmsg'))
        post('account', {
            username: form.email.value,
            password: form.password.value,
            api: form.api.value
        }, null, validateLogin)
    return false

validateLogin = (json, state) ->
    if json.loginRequired
        document.getElementById('loginmsg').innerHTML = json.error
    else
      if json.apiversion and json.apiversion >= 3
         if document.referrer and document.referrer.match(/https:\/\/(?:www)?\.snoot\.io\/dashboard/i)
            location.href = document.referrer
         else
            location.href = "/dashboard.html?page=default"
      else
         location.href = "/api2.html?page=default"

doResetPass = () ->
    rtoken = get('rtoken').value
    newpass = get('newpass').value
    post('account',{ remail: remail, rtoken: rtoken, newpass: newpass } , null, pwReset)
    return false

remail = ""
pwReset = () ->
   get('resetform').innerHTML = "Assuming you entered the right token, your password has now been reset!. <a href='login.html'>Log in</a>."

getResetToken = (json, state) ->
    form = get('resetform')
    form.innerHTML = ""
    p = mk('p', {}, "A reset token has been sent to your email address. Please enter the reset token and your new preferred password below:")
    app(form, p)
    token = mk('input', {type: 'text', placeholder: 'Reset token', autocomplete: 'off', name: 'rtoken', id: 'rtoken'})
    newpw = mk('input', {type: 'password', placeholder: 'New passord', autocomplete: 'off', name: 'newpass', id: 'newpass'})
    app(form, token)
    app(form, mk('br'))
    app(form, newpw)
    app(form, mk('br'))
    btn = mk('input', { type: 'button', onclick: 'doResetPass()', value: 'Reset your password'})
    form.setAttribute("onsubmit", "return doResetPass();")
    app(form, btn)
    
resetpw = () ->
    email = get('email').value
    remail = email
    post('account',{ reset: email } , null, getResetToken)
    return false
   
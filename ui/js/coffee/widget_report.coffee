rcollate = (list) ->
    out = ""
    while list.length > 2
        line = list.shift()
        out += line + ", "
    if list.length > 1
        out += list[0] + " and " + list[1]
    else
        return list[0]
    return out

report = (json, state) ->
        div = document.createElement('div')
        state.widget.inject(div, true)
        
        
        # Get + write the age of the project, if possible
        if json.projectAge == 0
            app(div, mk('h3', {}, "We were unable to determine the age of this project, sorry!"))
            return
        ageInMonths = parseInt(json.projectAge / (86400*30.3))
        ageInYears = parseInt(json.projectAge / (86400*365.25))
        age = mk('h3', {}, "Estimated age of project: #{ageInMonths} months (#{ageInYears} years)")
        app(div, age)
        
        
        # Commit rate trends
        if ageInYears >= 1
            title = mk('h2', {}, "Long range trends:")
            
            app(div, title)
            
            # Commits
            stitle = mk('h3', {}, "Commits:")
            carr = []
            
            # 5 year commit trend
            if ageInYears >= 5
                pct = json.commits['5'].angle
                rtext = "a rapid decline in commits in the long term (5+ years)"
                if pct > -50
                    rtext = "a moderate decline in commits in the long term (5+ years)"
                if pct > -30
                    rtext = "a slow decline in commits in the long term (5+ years)"
                if pct > -10
                    rtext = "a steady rate of commits in the long term (5+ years)"
                if pct > 10
                    rtext = "a slow increase in commits in the long term (5+ years)"
                if pct > 30
                    rtext = "a moderate increase in commits in the long term (5+ years)"
                if pct > 50
                    rtext = "a strong increase in commits in the long term (5+ years)"
                carr.push(rtext)
            
            # 2 year commit trend
            if ageInYears >= 2
                pct = json.commits['2'].angle
                rtext = "a rapid decline in commits in the medium term (2 years)"
                if pct > -50
                    rtext = "a moderate decline in commits in the medium term (2 years)"
                if pct > -30
                    rtext = "a slow decline in commits in the medium term (2 years)"
                if pct > -10
                    rtext = "a steady rate of commits in the medium term (2 years)"
                if pct > 10
                    rtext = "a slow increase in commits in the medium term (2 years)"
                if pct > 30
                    rtext = "a moderate increase in commits in the medium term (2 years)"
                if pct > 50
                    rtext = "a strong increase in commits in the medium term (2 years)"
                carr.push(rtext)
            
            # 1 year commit trend
            if ageInYears >= 1
                pct = json.commits['1'].angle
                rtext = "a rapid decline in commits in the short term (past year)"
                if pct > -50
                    rtext = "a moderate decline in commits in the short term (past year)"
                if pct > -30
                    rtext = "a slow decline in commits in the short term (past year)"
                if pct > -10
                    rtext = "a steady rate of commits in the short term (past year)"
                if pct > 10
                    rtext = "a slow increase in commits in the short term (past year)"
                if pct > 30
                    rtext = "a moderate increase in commits in the short term (past year)"
                if pct > 50
                    rtext = "a strong increase in commits in the short term (past year)"
                carr.push(rtext)
                
            p = mk('p', {}, "This project has experienced " + rcollate(carr) + ".")
            app(div, stitle)
            app(div, p)
            
            # Contributors
            stitle = mk('h3', {}, "Contributors:")
            carr = []
            
            # 5 year commit trend
            if ageInYears >= 5
                pct = json.authors['5'].authors.angle
                rtext = "a rapid decline in contributors in the long term (5+ years)"
                if pct > -50
                    rtext = "a moderate decline in contributors in the long term (5+ years)"
                if pct > -30
                    rtext = "a slow decline in contributors in the long term (5+ years)"
                if pct > -10
                    rtext = "a steady rate of contributors in the long term (5+ years)"
                if pct > 10
                    rtext = "a slow increase in contributors in the long term (5+ years)"
                if pct > 30
                    rtext = "a moderate increase in contributors in the long term (5+ years)"
                if pct > 50
                    rtext = "a strong increase in contributors in the long term (5+ years)"
                carr.push(rtext)
            
            # 2 year commit trend
            if ageInYears >= 2
                pct = json.authors['2'].authors.angle
                rtext = "a rapid decline in contributors in the medium term (2 years)"
                if pct > -50
                    rtext = "a moderate decline in contributors in the medium term (2 years)"
                if pct > -30
                    rtext = "a slow decline in contributors in the medium term (2 years)"
                if pct > -10
                    rtext = "a steady rate of contributors in the medium term (2 years)"
                if pct > 10
                    rtext = "a slow increase in contributors in the medium term (2 years)"
                if pct > 30
                    rtext = "a moderate increase in contributors in the medium term (2 years)"
                if pct > 50
                    rtext = "a strong increase in contributors in the medium term (2 years)"
                carr.push(rtext)
            
            # 1 year commit trend
            if ageInYears >= 1
                pct = json.authors['1'].authors.angle
                rtext = "a rapid decline in contributors in the short term (past year)"
                if pct > -50
                    rtext = "a moderate decline in contributors in the short term (past year)"
                if pct > -30
                    rtext = "a slow decline in contributors in the short term (past year)"
                if pct > -10
                    rtext = "a steady rate of contributors in the short term (past year)"
                if pct > 10
                    rtext = "a slow increase in contributors in the short term (past year)"
                if pct > 30
                    rtext = "a moderate increase in contributors in the short term (past year)"
                if pct > 50
                    rtext = "a strong increase in contributors in the short term (past year)"
                carr.push(rtext)
                
                active = parseInt(json.authors['1'].authors.average)
                carr.push("currently has #{active} active contributors")
            p = mk('p', {}, "The project has had " + rcollate(carr) + ".")
            app(div, stitle)
            app(div, p)
            
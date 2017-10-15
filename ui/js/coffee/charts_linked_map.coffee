
charts_linked = (obj, nodes, links, options) ->
  llcolors = genColors(nodes.length+1, 0.55, 0.475, true)
  licolors = genColors(nodes.length+1, 0.375, 0.35, true)
  lla = 0
  obj.className = "chartChart linkedChart"
  svg = d3.select(obj).append("svg")
    .attr("width", "100%")#llwidth)
    .attr("height", "600")# llheight)
  g = svg.append("g")
  bb = obj.getBoundingClientRect()
  llwidth = bb.width
  llheight = Math.max(600, bb.height)
  
  tooltip = d3.select("body").append("div")	
    .attr("class", "link_tooltip")				
    .style("opacity", 0);
  
  avg = links.length / nodes.length
  
  force = d3.layout.force()
      .gravity(0.015)
      .distance(llheight/8)
      .charge(-200/Math.log10(nodes.length))
      .linkStrength(0.2/avg)
      .size([llwidth, llheight])
  
  edges = []
  links.forEach((e) ->
    sourceNode = nodes.filter((n) => n.id == e.source)[0]
    targetNode = nodes.filter((n) => n.id == e.target)[0]
    edges.push({source: sourceNode, target: targetNode, s: e.source, value: e.value, name: e.name, tooltip: e.tooltip});
  )
  
  force
      .nodes(nodes)
      .links(edges)
      .start()
  lcolors = {}
  nodes.forEach((e) ->
    lcolors[e.id] = licolors[lla++]
    
  )
  lla = 0
  link = g.selectAll(".link")
      .data(edges)
      .enter().append("path")
      .attr("class", "link_link")
      .attr("id", (d) => d.name)
      .attr("data-source", (d) => d.source.id)
      .attr("data-target", (d) => d.target.id)
      .attr("style", (d) =>
        "stroke-width: #{d.value}; stroke: #{lcolors[d.s]};"
      ).on("mouseover", (d) ->
        if d.tooltip
            tooltip.transition()		
                .duration(100)		
                .style("opacity", .9);		
            tooltip.html("<b>#{d.name}:</b><br/>" + d.tooltip.replace("\n", "<br/>"))
                .style("left", (d3.event.pageX + 20) + "px")		
                .style("top", (d3.event.pageY - 28) + "px");	
            )
      .on("mouseout", (d) ->
            d3.select(this).style("stroke-opacity", "0.375")
            tooltip.transition()		
                .duration(200)		
                .style("opacity", 0);	
      )

   
  defs = svg.append("defs")
  nodes.forEach( (n) ->
    if n.gravatar
      defs.append("pattern")
      .attr("id", "gravatar-" + n.id)
      .attr("patternUnits", "userSpaceOnUse")
      .attr("width", n.size*2)
      .attr("height", n.size*2)
      .attr("x", n.size)
      .attr("y", n.size)
      .append("image")
      .attr("width", n.size*2)
      .attr("height", n.size*2)
      .attr("x", "0")
      .attr("y", "0")
      .attr("xlink:href", "https://secure.gravatar.com/avatar/#{n.gravatar}.png?d=identicon")
    else
      n.gravatar = false
  )  
  
  node = g.selectAll(".node")
      .data(nodes)
    .enter().append("g")
      .attr("class", "link_node")
      .attr("data-source", (d) => d.id)
      .call(force.drag);
  
  lTargets = []
  
  gatherTargets = (d, e) ->
    if e.source == d or e.target == d
      lTargets.push(e.source.id)
      lTargets.push(e.target.id)
      return true
    return false
  
  uptop = svg.append("g")
  x = null
 
  node.append("circle")
      .attr("class", "link_node")
      .attr("data-source", (d) => d.id)
      .attr("data-color", (d) =>
        lla++
        return llcolors[lla-1]
      )
      .style("fill", (d) ->
        if d.gravatar
          return "url(#gravatar-#{d.id})"
        else
          return "#{d3.select(this).attr('data-color')}"
      )
      .style("stroke", "black")
      .attr("r", (d) => d.size)
      .on("mouseover", (d) ->
        lTargets.push(d.id)
        d3.selectAll("path").style("stroke-opacity", "0.075")
        d3.selectAll("path").filter((e) => gatherTargets(d,e) ).style("stroke-opacity", "1").style("z-index", "20")
        d3.selectAll("path").filter((e) => e.source == d or e.target).each((o) =>
          
          x = d3.select(this).insert("g", ":first-child").style("stroke", "red !important")
          x.append("use").attr("xlink:href", "#" + o.name)
        )
        d3.selectAll("circle").filter((e) => e.id not in lTargets ).style("opacity", "0.2")
        d3.selectAll("text").filter((e) => e.id not in lTargets ).style("opacity", "0.2")
        )
      .on("mouseout", (d) ->
        lTargets = []
        if x
          x.selectAll("*").remove()
        d3.selectAll("circle").style("opacity", null)
        d3.selectAll("text").style("opacity", null)
        d3.selectAll("path").style("stroke-opacity", null)
        )
  
  

  node.append("a")
      .attr("href", (d) => if not d.gravatar then "#" else "contributors.html?page=biography&email=#{d.id}")
      .append("text")
      .attr("dx", 13)
      .attr("dy", ".35em")
      .text((d) => d.name)      
      .on("mouseover", (d) ->
        if d.tooltip
            tooltip.transition()		
                .duration(100)		
                .style("opacity", .9);		
            tooltip.html("<b>#{d.name}:</b><br/>" + d.tooltip.replace("\n", "<br/>"))
                .style("left", (d3.event.pageX + 20) + "px")		
                .style("top", (d3.event.pageY - 28) + "px");	
            )
      .on("mouseout", (d) ->
            #d3.selectAll(".link").filter( (e) => e.source == this.id ).style("stroke-opacity", "0.375")
            tooltip.transition()		
                .duration(200)		
                .style("opacity", 0);	
      )

  
  force.on("tick", () ->
    link.attr("d", (d) ->
        dx = d.target.x - d.source.x
        dy = d.target.y - d.source.y
        dr = Math.sqrt(dx * dx + dy * dy)
        return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1 " + d.target.x + "," + d.target.y
    )
    node.attr("cx",(d) =>
        d.x = Math.max(d.size, Math.min(llwidth - d.size, d.x))
        )
      .attr("cy", (d) =>
        d.y = Math.max(d.size, Math.min(llheight - d.size, d.y))
      )
    node.attr("transform", (d) => ("translate(" + d.x + "," + d.y + ")"))
  )
  linked_zoom = () ->
        isShift = not not window.event.shiftKey
        if isShift
          g.attr("transform", "translate("+d3.event.translate + ")scale(" + d3.event.scale + ")");
        else
          g.attr("transform", "scale(" + d3.event.scale + ")");
  svg
    .call( d3.behavior.zoom().center([llwidth / 2, llheight / 2]).scaleExtent([0.333, 4]).on("zoom", linked_zoom)  )

  
  return [
    {
      svg: svg,
      parent: obj,
      force: force,
      config: {},
      resize: (conf) ->
        ns = ""
        if conf.height
          ns += "height: #{conf.height}px; "
        if conf.width
          ns += "width: #{conf.width}px; "
        svg.attr("style", ns)
        llwidth = parseInt(svg.style("width"))
        llheight = parseInt(svg.style("height"))
        force.size([llwidth, llheight]).distance(llheight/4)
        force
        .nodes(nodes)
        .links(edges)
        .start()
    },
    {linked: true}]



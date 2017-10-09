
charts_linked = (obj, nodes, links, options) ->
  llcolors = genColors(nodes.length+1, 0.55, 0.475, true)
  lla = 0
  svg = d3.select(obj).append("svg")
    .attr("width", "100%")#llwidth)
    .attr("height", "720")# llheight)
  g = svg.append("g")
  obj.style.minHeight = "600px"
  bb = obj.getBoundingClientRect()
  llwidth = bb.width
  llheight = bb.height
  force = d3.layout.force()
      .gravity(.05)
      .distance(llheight/8)
      .charge(-80)
      .size([llwidth, llheight])

  edges = []
  links.forEach((e) ->
    sourceNode = nodes.filter((n) => n.id == e.source)[0]
    targetNode = nodes.filter((n) => n.id == e.target)[0]
    edges.push({source: sourceNode, target: targetNode, value: e.value});
  )
  
  force
      .nodes(nodes)
      .links(edges)
      .start()

  link = g.selectAll(".link")
      .data(edges)
      .enter().append("path")
      .attr("class", "link_link")
      .attr("style", (d) =>
        "stroke-width: #{d.value};"
      )

  node = g.selectAll(".node")
      .data(nodes)
    .enter().append("g")
      .attr("class", "link_node")
      .call(force.drag);

  node.append("circle")
      .attr("class", "link_node")
      .attr("style", (d) ->
        lla++
        return "fill: #{llcolors[lla-1]};"
      )
      .attr("r", (d) -> d.size);

  node.append("svg:a")
      .attr("xlink:href", (d) => d.name)
      .append("text")
      .attr("dx", 12)
      .attr("dy", ".35em")
      .text((d) => d.name)

  
  force.on("tick", () ->
    link.attr("d", (d) ->
        dx = d.target.x - d.source.x
        dy = d.target.y - d.source.y
        dr = Math.sqrt(dx * dx + dy * dy)
        return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1 " + d.target.x + "," + d.target.y
    )
  
    node.attr("transform", (d) => ("translate(" + d.x + "," + d.y + ")"))
  )
  linked_zoom = () ->
        g.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
  svg
    .call( d3.behavior.zoom().scaleExtent([0.5, 4]).on("zoom", linked_zoom)  )

    
  
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



charts_linked = (obj, nodes, links, options) ->
  llcolors = genColors(nodes.length+1, 0.55, 0.475, true)
  lla = 0
  svg = d3.select(obj).append("svg")
    .attr("width", "100%")#llwidth)
    .attr("height", "720")# llheight)
  obj.style.minHeight = "600px"
  bb = obj.getBoundingClientRect()
  llwidth = bb.width
  llheight = bb.height
  force = d3.layout.force()
      .gravity(.25)
      .distance(llheight/4)
      .charge(-50)
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

  link = svg.selectAll(".link")
      .data(edges)
      .enter().append("line")
      .attr("class", "link_link")
      .attr("style", (d) =>
        "stroke-width: #{d.value};"
      )

  node = svg.selectAll(".node")
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
    link.attr("x1", (d) => d.source.x;)
        .attr("y1", (d) => d.source.y;)
        .attr("x2", (d) => d.target.x;)
        .attr("y2", (d) => d.target.y;)
    node.attr("transform", (d) => ("translate(" + d.x + "," + d.y + ")"))
  )
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
        force.size([llwidth, llheight]).distance(llheight/2)
        force
        .nodes(nodes)
        .links(edges)
        .start()
    },
    {linked: true}]



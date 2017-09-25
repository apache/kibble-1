charts_radarchart = (obj, data, options) ->
		cfg = {
			radius: 5,
			w: 360,
			h: 360,
			factor: 1,
			factorLegend: .85,
			levels: 4,
			maxValue: 100,
			radians: 2 * Math.PI,
			opacityArea: 0.5,
			ToRight: 5,
			TranslateX: 30,
			TranslateY: 30,
			ExtraWidthX: 200,
			ExtraWidthY: 100,
			color: genColors(16, 0.55, 0.475, true)
		 }
		LegendOptions = []
		d = data
		if data.indicators and data.data
			d = []
			for el, i in data.data
				li = []
				LegendOptions.push(el.name)
				for indicator, j in data.indicators
					li.push({axis: indicator, value: el.value[j]})
				d.push(li)

		cfg.maxValue = Math.max(cfg.maxValue, d3.max(d, (i) => d3.max(i.map((o) => o.value))))
		axes = (d[0].map((i, j) => i.axis))
		total = axes.length;
		radius = cfg.factor*Math.min(cfg.w/2, cfg.h/2);
		Format = (edge) =>
			Math.floor((edge/24)+0.5) + "↑ (" + (5**(edge/24)).pretty() + ")"
		d3.select(obj).select("svg").remove();
		
		rect = obj.getBoundingClientRect()
		g = d3.select(obj)
				.append("svg")
				.attr("preserveAspectRatio", "xMinYMin meet")
				.attr("viewBox", "0 0 1000 500")
				.append("g")
				.attr("transform", "translate(" + cfg.TranslateX + "," + cfg.TranslateY + ")");
				;
	
		# Indicator lines
		for j in [0...cfg.levels]
			levelFactor = cfg.factor * radius * ( (j+1) / cfg.levels)
			g.selectAll(".levels")
			 .data(axes)
			 .enter()
			 .append("svg:line")
			 .attr("x1", (d, i) => levelFactor*(1-cfg.factor*Math.sin(i*cfg.radians/total)))
			 .attr("y1", (d, i) => levelFactor*(1-cfg.factor*Math.cos(i*cfg.radians/total)))
			 .attr("x2", (d, i) => levelFactor*(1-cfg.factor*Math.sin((i+1)*cfg.radians/total)))
			 .attr("y2", (d, i) => levelFactor*(1-cfg.factor*Math.cos((i+1)*cfg.radians/total)))
			 .attr("class", "line")
			 .style("stroke", "grey")
			 .style("stroke-opacity", "0.75")
			 .style("stroke-width", "0.3px")
			 .attr("transform", "translate(" + (cfg.w/2-levelFactor) + ", " + (cfg.h/2-levelFactor) + ")")
		
	
		# Levels
		for j in [0...cfg.levels]
			levelFactor = cfg.factor*radius*((j+1)/cfg.levels);
			g.selectAll(".levels")
			 .data([1])
			 .enter()
			 .append("svg:text")
			 .attr("x", (d) => levelFactor*(1-cfg.factor*Math.sin(0)))
			 .attr("y", (d) => levelFactor*(1-cfg.factor*Math.cos(0)))
			 .attr("class", "legend")
			 .style("font-family", "sans-serif")
			 .style("font-size", "10px")
			 .attr("transform", "translate(" + (cfg.w/2-levelFactor + cfg.ToRight) + ", " + (cfg.h/2-levelFactor) + ")")
			 .attr("fill", "#737373")
			 .text(Format((j+1)*cfg.maxValue/cfg.levels))
		
		
		series = 0
	
		axis = g.selectAll(".axis")
				.data(axes)
				.enter()
				.append("g")
				.attr("class", "axis")
	
		axis.append("line")
			.attr("x1", cfg.w/2)
			.attr("y1", cfg.h/2)
			.attr("x2", (d,i) => cfg.w/2*(1-cfg.factor*Math.sin(i*cfg.radians/total)))
			.attr("y2", (d,i) => cfg.h/2*(1-cfg.factor*Math.cos(i*cfg.radians/total)))
			.attr("class", "line")
			.style("stroke", "grey")
			.style("stroke-width", "1px");
	
		axis.append("text")
			.attr("class", "legend")
			.text((d) => d)
			.style("font-family", "sans-serif")
			.style("font-size", "11px")
			.attr("text-anchor", "middle")
			.attr("dy", "1.5em")
			.attr("transform", (d,i) => "translate(0, -10)")
			.attr("x", (d,i) => cfg.w/2*(1-cfg.factorLegend*Math.sin(i*cfg.radians/total))-60*Math.sin(i*cfg.radians/total))
			.attr("y", (d,i) => cfg.h/2*(1-Math.cos(i*cfg.radians/total))-20*Math.cos(i*cfg.radians/total))
	
	 
		d.forEach((y,x) ->
			dataValues = []
			g.selectAll(".nodes")
			 .data(y, (j,i) ->
				 #alert(j,i)
				 dataValues.push(\
					[\
					cfg.w/2*(1-(parseFloat(Math.max(j.value, 0))/cfg.maxValue)*cfg.factor*Math.sin(i*cfg.radians/total)),\
					cfg.h/2*(1-(parseFloat(Math.max(j.value, 0))/cfg.maxValue)*cfg.factor*Math.cos(i*cfg.radians/total))\
					]\
					)
			 )
			
			dataValues.push(dataValues[0])
			
			g.selectAll(".area")
				.data([dataValues])
				.enter()
				.append("polygon")
				.attr("class", "radar-chart-serie"+series)
				.style("stroke-width", "2px")
				.style("stroke", cfg.color[series])
				.attr("points", (d) ->
					str=""
					#alert(d)
					for pt in d
						str=str+pt[0]+","+pt[1]+" ";
					return str
				 )
				.style("fill", (j,i) => cfg.color[series])
				.style("fill-opacity", cfg.opacityArea)
				.on('mouseover', (d) ->
								 z = "polygon."+d3.select(this).attr("class");
								 g.selectAll("polygon")
									.transition(200)
									.style("fill-opacity", 0.1); 
								 g.selectAll(z)
									.transition(200)
									.style("fill-opacity", .7);
				 )
				.on('mouseout', () ->
								 g.selectAll("polygon")
									.transition(200)
									.style("fill-opacity", cfg.opacityArea);
				 )
			series++
		)
		
		series = 0
		
		d.forEach( (y,x) ->
			g.selectAll(".nodes")
			.data(y).enter()
			.append("svg:circle")
			.attr("class", "radar-chart-serie"+series)
			.attr('r', cfg.radius)
			.attr("alt", (j) => Math.max(j.value, 0))
			.attr("cx", (j,i) ->
				dataValues = dataValues || []
				dataValues.push([
						cfg.w/2*(1-(parseFloat(Math.max(j.value, 0))/cfg.maxValue)*cfg.factor*Math.sin(i*cfg.radians/total)), 
						cfg.h/2*(1-(parseFloat(Math.max(j.value, 0))/cfg.maxValue)*cfg.factor*Math.cos(i*cfg.radians/total))
				])
				return cfg.w/2*(1-(Math.max(j.value, 0)/cfg.maxValue)*cfg.factor*Math.sin(i*cfg.radians/total))
			)
			.attr("cy", (j,i) ->
				return cfg.h/2*(1-(Math.max(j.value, 0)/cfg.maxValue)*cfg.factor*Math.cos(i*cfg.radians/total))
			)
			.attr("data-id",  (j) => j.axis)
			.style("fill", cfg.color[series]).style("fill-opacity", .9)
			.on('mouseover', (d) ->
						newX =  parseFloat(d3.select(this).attr('cx')) - 10
						newY =  parseFloat(d3.select(this).attr('cy')) - 5
						
						tooltip
							.attr('x', newX)
							.attr('y', newY)
							.text(Format(d.value))
							.transition(200)
							.style('opacity', 1)
							
						z = "polygon."+d3.select(this).attr("class");
						g.selectAll("polygon")
							.transition(200)
							.style("fill-opacity", 0.1)
						g.selectAll(z)
							.transition(200)
							.style("fill-opacity", .7)
						)
			.on('mouseout', () ->
						tooltip
							.transition(200)
							.style('opacity', 0);
						g.selectAll("polygon")
							.transition(200)
							.style("fill-opacity", cfg.opacityArea);
						)
			.append("svg:title")
			.text((j) => Math.max(j.value, 0));
	
			series++
		);
		
		# Tooltip
		tooltip = g.append('text')
					 .style('opacity', 0)
					 .style('font-family', 'sans-serif')
					 .style('font-size', '13px');
		
		legend = g.append("g")
		.attr("class", "legend")
		.attr("height", 100)
		.attr("width", 200)
		.attr('transform', 'translate(90,20)') 
		
		
		legend.selectAll('rect')
			.data(LegendOptions)
			.enter()
			.append("rect")
			.attr("x", cfg.w - 65)
			.attr("y", (d,i) => i * 20)
			.attr("width", 10)
			.attr("height", 10)
			.style("fill", (d,i) => cfg.color[i])
			
		
		legend.selectAll('text')
			.data(LegendOptions)
			.enter()
			.append("text")
			.attr("x", cfg.w - 52)
			.attr("y",(d, i) => (i * 20 + 9))
			.attr("font-size", "11px")
			.attr("fill", "#737373")
			.text((d) => d)
			
		g.resize = () -> return true
		return [g, {}]
	

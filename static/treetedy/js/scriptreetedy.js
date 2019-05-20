$(document).ready(function() {
	var svg = d3.select("svg"),
		width = +svg.attr("width"),
		height = +svg.attr("height"),
		g = svg.append("g").attr("transform", "translate(" + (width / 2 + 40) + "," + (height / 2 + 90) + ")");

	var tree = d3.cluster()
		.size([360, 500])
		.separation(function(a, b) { return (a.parent == b.parent ? 1 : 2) / a.depth; });

	var stratify = d3.stratify()
		.parentId(function(d) { return d.id.substring(0, d.id.lastIndexOf(".")); });

	var JsonFile = null;	
	d3.json("./static/upload/1.json", function(error, jsonfile) {
	  if (error) throw error;
	  
	  JsonFile = jsonfile;  
	});
	
	var array_palabras = [];
	var array_obj = [];

	d3.json("./static/upload/base.json", function(error, treeDatas) {
		if (error) throw error;
		
		//var treeData = treeDatas;
		var treeDatass = JSON.parse(JSON.stringify(treeDatas));
		
		var monto = 0;
		
		$.each(JsonFile, function(key, val) {
			if (typeof val.keywords !== 'undefined') {
				$.each(val.keywords.split(","), function( index, value ) {
					array_palabras.push([value,val.title]);
				});	
			}
		});

		//console.log(array_palabras);
		//console.log(treeDatass);
		
		$.each(treeDatas.children, function(key, val) {
			if (!val.hasOwnProperty("children")) {
				var flag = 0;
				$.each(array_palabras, function(index, value){
					//if(val.name == value[0]) {
					if(val.name.trim().toLowerCase() == value[0].trim().toLowerCase()) {	
						if(flag == 0) {
							treeDatass.children[key - monto].children = [{"name": value[1]}];
						} else {
							treeDatass.children[key - monto].children.push({"name": value[1]});
						}
						
						flag = flag + 1;
						//console.log(treeDatass.children[key-monto]);
					}
				});
				if(flag == 0) {
					delete treeDatass.children.splice(key-monto,1);
					monto = monto + 1;
					
					//console.log(treeData);
				}
			} else {
				var monto2 = 0;
				$.each(val.children, function(key2, val2) {
					var flag2 = 0;
					$.each(array_palabras, function(index2, value2){
						//if(val2.name == value2[0]) {
						if(val2.name.trim().toLowerCase() == value2[0].trim().toLowerCase()) {
							if(flag2 == 0) {
								treeDatass.children[key - monto].children[key2 - monto2].children = [{"name": value2[1]}];
							} else {
								treeDatass.children[key - monto].children[key2 - monto2].children.push({"name": value2[1]});
							}
							//console.log(treeDatass);	
							flag2 = flag2 + 1;
						}
					});
					if(flag2 == 0) {
						delete treeDatass.children[key - monto].children.splice(key2 - monto2,1);
						monto2 = monto2 + 1;
						//console.log(treeDatass);
					}
				});
			}
		});
		
		var treeData = JSON.parse(JSON.stringify(treeDatass));
		var montin = 0;
		
		$.each(treeDatass.children, function(key3, val3) {
			if (val3.hasOwnProperty("children") && val3.children.length == 0) {
				delete treeData.children.splice(key3-montin,1);
				montin = montin + 1;
			}
		});
	
		var root = d3.hierarchy(treeData);
		tree(root);

		var link = g.selectAll(".link")
			.data(root.descendants().slice(1))
			.enter().append("path")
			.attr("class", "link")
			.attr("d", function(d) {
				return "M" + project(d.x, d.y)
				+ "C" + project(d.x, (d.y + d.parent.y) / 2)
				+ " " + project(d.parent.x, (d.y + d.parent.y) / 2)
				+ " " + project(d.parent.x, d.parent.y);
			});

		var node = g.selectAll(".node")
			.data(root.descendants())
			.enter().append("g")
			.attr("class", function(d) { return "node" + (d.children ? " node--internal" : " node--leaf"); })
			.attr("transform", function(d) { return "translate(" + project(d.x, d.y) + ")"; });

		node.append("circle")
		  .attr("r", 2.5);
		
		node.append("text")
		  .attr("dy", ".31em")
		  .attr("x", function(d) { return d.x < 180 === !d.children ? 6 : -6; })
		  .style("text-anchor", function(d) { return d.x < 180 === !d.children ? "start" : "end"; })
		  .attr("transform", function(d) { return "rotate(" + (d.x < 180 ? d.x - 90 : d.x + 90) + ")"; })
		  //.text(function(d) { return d.id.substring(d.id.lastIndexOf(".") + 1); });
		  .text(function(d) { return d.data.name });
	});

	function project(x, y) {
		var angle = (x - 90) / 180 * Math.PI, radius = y;
		return [radius * Math.cos(angle), radius * Math.sin(angle)];
	}
});
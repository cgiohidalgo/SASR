$(document).ready(function() {
	var r = 1100 / 2;

	var tree = d3.layout.tree()
		.size([360, r - 150])
		.separation(function(a, b) { return (a.parent == b.parent ? 1 : 2) / a.depth; });

	var diagonal = d3.svg.diagonal.radial()
		.projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });

	var vis = d3.select("#chart").append("svg:svg")
		.attr("width", r * 2)
		.attr("height", r * 2 + 170)
		.append("svg:g")
		.attr("transform", "translate(" + r + "," + r + ")");

	var JsonFile = null;	
	
	d3.json("/uncode/static/upload/1.json", function(jsonfile) {
	  //if (error) throw error;
	  
	  JsonFile = jsonfile;  
	});
	
	var array_palabras = [];
	var array_obj = [];

	d3.json("/uncode/static/upload/base.json", function(treeDatas) {
		//if (error) throw error;
		
		//var treeData = treeDatas;
		var treeDatass = JSON.parse(JSON.stringify(treeDatas));
		
		var monto = 0;
		
		$.each(JsonFile, function(key, val) {
			if (typeof val.keywords !== 'undefined') {
				$.each(val.keywords.split(","), function( index, value ) {
					val.doi!==undefined?array_palabras.push([value,val.doi]):array_palabras.push([value,val.url]);
					val.url!==undefined?array_palabras.push([value,val.url]):array_palabras.push([value,val.title]);
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
	
		var nodes = tree.nodes(treeData);
 
		var link = vis.selectAll("path.link")
			.data(tree.links(nodes))
			.enter().append("svg:path")
			.attr("class", "link")
			.attr("d", diagonal);

		var node = vis.selectAll("g.node")
			.data(nodes)
			.enter().append("svg:g")
			.attr("class", "node")
			.attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")"; })
 
		node.append("svg:circle").attr("r", 4.5);
 
		node.append("svg:text")
			.attr("dx", function(d) { return d.x < 180 ? 8 : -8; })
			.attr("dy", ".31em")
			.attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
			.attr("transform", function(d) { return d.x < 180 ? null : "rotate(180)"; })
			.text(function(d) { return d.name; });
	});
});
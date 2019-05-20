var script = document.createElement('script');
    script.type = 'text/javascript';

    script.src = 'https://d3js.org/d3.v4.min.js';
    document.body.appendChild(script);

var svg = d3.select("svg"),
	width = +svg.attr("width"),
	height = +svg.attr("height"),
	g = svg.append("g").attr("transform", "translate(" + (width / 2 + 40) + "," + (height / 2 + 90) + ")");

var stratify = d3.stratify()
	.parentId(function(d) { return d.id.substring(0, d.id.lastIndexOf(".")); }) (svg);

var tree = d3.tree()
	.size([360, 500])
	.separation(function(a, b) { return (a.parent == b.parent ? 1 : 2) / a.depth; });

d3.csv("./static/upload/rad.csv", function(error, data) {
  if (error) throw error;

  var root = tree(stratify(data));

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
	  .text(function(d) { return d.id.substring(d.id.lastIndexOf(".") + 1); });
});

function project(x, y) {
  var angle = (x - 90) / 180 * Math.PI, radius = y;
  return [radius * Math.cos(angle), radius * Math.sin(angle)];
}
// Add a title
// sSvg.append("text")
//    .attr("transform", "translate(100,0)")
//    .attr("x", 140)
//    .attr("y", 50)
//    .attr("font-size", "24px")
//    .text("Boulder Sends");


let bSvg = d3.select("#boulder"),
    bMargin = 200,
    bWidth = bSvg.attr("width") - bMargin,
    bHeight = bSvg.attr("height") - bMargin;

let bxAxis = d3.scaleBand().range([0, bWidth]).padding(0.4),
    byAxis = d3.scaleLinear().range([bHeight, 0]);

let bgSvg = bSvg.append("g")
        .attr("transform", "translate(" + 100 + "," + 100 + ")");


function buildBoulderGraph(data) {

    bxAxis.domain(data.map(function(d) { return d.grade; }));
    byAxis.domain([0, d3.max(data, function(d) { return d.sends; })]);

    // build x axis
    bgSvg.append("g")
        .attr("transform", "translate(0," + bHeight + ")")
        .call(d3.axisBottom(bxAxis))
        .append("text")
        .attr("y", bHeight - 250)
        .attr("x", bWidth - 220)
        .attr("text-anchor", "end")
        .attr("fill", "#002433")
        .attr("font-size", "28px")
        .text("Grade");

    // build y axis
    bgSvg.append("g")
        .call(d3.axisLeft(byAxis).tickFormat(function(d){
            return d;
        }).ticks(5))
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 80)
        .attr("x", -100)
        .attr("dy", "-5.1em")
        .attr("text-anchor", "end")
        .attr("fill", "#002433")
        .attr("font-size", "28px")
        .text("Sends");

    // add bars
    bgSvg.selectAll(".bar")
        .data(data)
        .enter().append("rect")
        .attr("class", "bar")
        .attr("fill", "#002433")
        .on("mouseover", bOnMouseOver) //Add listener for the mouseover event
        .on("mouseout", bOnMouseOut)   //Add listener for the mouseout event
        .attr("x", function(d) { return bxAxis(d.grade); })
        .attr("y", function(d) { return byAxis(d.sends); })
        .attr("width", bxAxis.bandwidth())
        .transition()
        .ease(d3.easeLinear)
        .duration(400)
        .delay(function (d, i) {
            return i * 50;
        })
        .attr("height", function(d) { return bHeight - byAxis(d.sends); });
};

// mouseover event handler function
function bOnMouseOver(d, i) {
    d3.select(this).attr('class', 'highlight');
    d3.select(this)
        .transition()     // adds animation
        .duration(400)
        .attr('width', bxAxis.bandwidth() + 5)
        .attr("y", function(d) { return byAxis(d.sends) - 10; })
        .attr("height", function(d) { return bHeight - byAxis(d.sends) + 10; })
        .attr("fill", "#00b3ff");

    bgSvg.append("text")
    .attr('class', 'val')
    .attr("fill", "#002433")
    .attr("font-size", "18px")
    .attr('x', function() {
        return bxAxis(d.grade);
    })
    .attr('y', function() {
        return byAxis(d.sends) - 15;
    })
    .text(function() {
        return [d.grade + ': \n' + d.sends];  // Value of the text
    });
}

// mouseout event handler function
function bOnMouseOut(d, i) {
    // use the text label class to remove label on mouseout
    d3.select(this).attr('class', 'bar');
    d3.select(this)
        .transition()     // adds animation
        .duration(400)
        .attr('width', bxAxis.bandwidth())
        .attr("y", function(d) { return byAxis(d.sends); })
        .attr("height", function(d) { return bHeight - byAxis(d.sends); })
        .attr("fill", "#002433");

    d3.selectAll('.val')
      .remove()
}

// buildGraph(graphData);

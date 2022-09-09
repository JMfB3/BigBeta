// Add a title
// sSvg.append("text")
//    .attr("transform", "translate(100,0)")
//    .attr("x", 140)
//    .attr("y", 50)
//    .attr("font-size", "24px")
//    .text("Boulder Sends");


let sSvg = d3.select("#sport"),
    sMargin = 200,
    sWidth = sSvg.attr("width") - sMargin,
    sHeight = sSvg.attr("height") - sMargin;

let sxAxis = d3.scaleBand().range([0, sWidth]).padding(0.4),
    syAxis = d3.scaleLinear().range([sHeight, 0]);

let sgSvg = sSvg.append("g")
        .attr("transform", "translate(" + 100 + "," + 100 + ")");


function buildSportGraph(data) {

    sxAxis.domain(data.map(function(d) { return d.grade; }));
    syAxis.domain([0, d3.max(data, function(d) { return d.sends; })]);

    // build x axis
    sgSvg.append("g")
        .attr("transform", "translate(0," + sHeight + ")")
        .call(d3.axisBottom(sxAxis))
        .append("text")
        .attr("y", sHeight - 250)
        .attr("x", sWidth - 220)
        .attr("text-anchor", "end")
        .attr("fill", "#002433")
        .attr("font-size", "28px")
        .text("Grade");

    // build y axis
    sgSvg.append("g")
        .call(d3.axisLeft(syAxis).tickFormat(function(d){
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
    sgSvg.selectAll(".bar")
        .data(data)
        .enter().append("rect")
        .attr("class", "bar")
        .attr("fill", "#002433")
        .on("mouseover", sOnMouseOver) //Add listener for the mouseover event
        .on("mouseout", sOnMouseOut)   //Add listener for the mouseout event
        .attr("x", function(d) { return sxAxis(d.grade); })
        .attr("y", function(d) { return syAxis(d.sends); })
        .attr("width", sxAxis.bandwidth())
        .transition()
        .ease(d3.easeLinear)
        .duration(400)
        .delay(function (d, i) {
            return i * 50;
        })
        .attr("height", function(d) { return sHeight - syAxis(d.sends); });
};

// mouseover event handler function
function sOnMouseOver(d, i) {
    d3.select(this).attr('class', 'highlight');
    d3.select(this)
        .transition()     // adds animation
        .duration(400)
        .attr('width', sxAxis.bandwidth() + 5)
        .attr("y", function(d) { return syAxis(d.sends) - 10; })
        .attr("height", function(d) { return sHeight - syAxis(d.sends) + 10; })
        .attr("fill", "#00b3ff");

    sgSvg.append("text")
    .attr('class', 'val')
    .attr("fill", "#002433")
    .attr("font-size", "18px")
    .attr('x', function() {
        return sxAxis(d.grade);
    })
    .attr('y', function() {
        return syAxis(d.sends) - 15;
    })
    .text(function() {
        return [d.grade + ': \n' + d.sends];  // Value of the text
    });
}

// mouseout event handler function
function sOnMouseOut(d, i) {
    // use the text label class to remove label on mouseout
    d3.select(this).attr('class', 'bar');
    d3.select(this)
        .transition()     // adds animation
        .duration(400)
        .attr('width', sxAxis.bandwidth())
        .attr("y", function(d) { return syAxis(d.sends); })
        .attr("height", function(d) { return sHeight - syAxis(d.sends); })
        .attr("fill", "#002433");

    d3.selectAll('.val')
      .remove()
}

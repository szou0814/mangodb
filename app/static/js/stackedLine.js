import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";

function StackedAreaChart(data, {
  x = ([x]) => x, // given d in data, returns the (ordinal) x-value
  y = ([, y]) => y, // given d in data, returns the (quantitative) y-value
  z = () => 1, // given d in data, returns the (categorical) z-value
  marginTop = 150, // top margin, in pixels
  marginRight = 30, // right margin, in pixels
  marginBottom = 30, // bottom margin, in pixels
  marginLeft = 80, // left margin, in pixels
  width = 740, // outer width, in pixels
  height = 400, // outer height, in pixels
  xType = d3.scaleUtc, // type of x-scale
  xDomain, // [xmin, xmax]
  xRange = [marginLeft, width - marginRight], // [left, right]
  yType = d3.scaleLinear, // type of y-scale
  yDomain, // [ymin, ymax]
  yRange = [height - marginBottom, marginTop], // [bottom, top]
  zDomain, // array of z-values
  offset = d3.stackOffsetDiverging, // stack offset method
  order = d3.stackOrderNone, // stack order method
  xFormat, // a format specifier string for the x-axis
  yFormat = ",.0f", // a format specifier for the y-axis
  yLabel, // a label for the y-axis
  colors = d3.quantize(d3.interpolateCool, 50), // array of colors for z
} = {}) {
  const STATE_NAMES = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri",
    "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
    "Wisconsin", "Wyoming"];

  var stackedStatus = true;
  var selectedState;

  // Compute values.
  var X = d3.map(data, x);
  var Y = d3.map(data, y);
  var Z = d3.map(data, z);

  // Compute default x- and z-domains, and unique the z-domain.
  if (xDomain === undefined) xDomain = d3.extent(X);
  if (zDomain === undefined) zDomain = Z;
  zDomain = new d3.InternSet(zDomain);

  // Omit any data not present in the z-domain.
  var I = d3.range(X.length).filter(i => zDomain.has(Z[i]));

  // Compute a nested array of series where each series is [[y1, y2], [y1, y2],
  // [y1, y2], …] representing the y-extent of each stacked rect. In addition,
  // each tuple has an i (index) property so that we can refer back to the
  // original data point (data[i]). This code assumes that there is only one
  // data point for a given unique x- and z-value.
  var series = d3.stack()
      .keys(zDomain)
      .value(([x, I], z) => Y[I.get(z)])
      .order(order)
      .offset(offset)
    (d3.rollup(I, ([i]) => i, i => X[i], i => Z[i]))
    .map(s => s.map(d => Object.assign(d, {i: d.data[1].get(s.key)})));

  // Compute the default y-domain. Note: diverging stacks can be negative.
  if (yDomain === undefined) yDomain = d3.extent(series.flat(2));

  // Construct scales and axes.
  var xScale = xType(0, xRange);
  var yScale = yType(yDomain, yRange);
  var color = d3.scaleOrdinal(zDomain, colors);

  var xAxis = d3.axisBottom(xScale).ticks(width / 80, xFormat).tickSizeOuter(0);
  var yAxis = d3.axisLeft(yScale).ticks(height / 50, yFormat);

  var area = d3.area()
      .x(({i}) => xScale(X[i]))
      .y0(([y1]) => yScale(y1))
      .y1(([, y2]) => yScale(y2));

  const svg = d3.create("svg")
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", [0, 0, width, height])
      .attr("style", "max-width: 100%; height: auto; height: intrinsic;");

  var yAxisGroup = svg.append("g")
      .attr("transform", `translate(${marginLeft},0)`)
      .call(yAxis)
      .call(g => g.select(".domain").remove())
      .call(g => g.selectAll(".tick line").clone()
          .attr("x2", width - marginLeft - marginRight)
          .attr("stroke-opacity", 0.1))

  var xAxisGroup = svg.append("g")
      .attr("transform", `translate(0,${height - marginBottom})`)
      .call(xAxis);

  var areaGroup = svg.append('g');

  const size = STATE_NAMES.length/6 * 1.2;
  const legend = svg.selectAll('.legendItems')
    .data(STATE_NAMES)
    .join("g")
    .attr("class", "legendItems")
    .on("mouseover", function() {
      d3.select(this)
        .style("cursor", "pointer")
        .select('text')
          .style("fill", 'red');
    })
    .on("mouseout", function(event, d) {
      if (selectedState != d) {
        d3.select(this)
          .style("cursor", "default")
          .select('text')
            .style("fill", 'white');
      }
    })
    .on("click", function(event, d) {
      chart.swapGraph(d);
      chart.update();

      if (selectedState == d) {
        d3.select(this)
          .style("cursor", "pointer")
          .select('text')
            .style("fill", 'red');
      }
    });

  legend
    .append("rect")
    .attr("x", function(d,i) { return (marginLeft-60) + (Math.floor(i/9) * (STATE_NAMES.length/4 * 9.9)) })
    .attr("y", function(d,i) { return Math.floor(i%9)*(size+5) })
    .attr("width", size)
    .attr("height", size)
    .style("fill", function(d) { return color(d) });

  legend
    .append("text")
    .attr("x", function(d,i) { return (marginLeft-60) + ((size*1.2) + (Math.floor(i/9) * (STATE_NAMES.length/4 * 9.9))) })
    .attr("y", function(d,i) { return Math.floor(i%9)*(size+5) + size/1.3 })
    .style("fill", 'white')
    .text(function(d) { return d })
    .attr("text-anchor", "left")
    .style("alignment-baseline", "middle")
    .style("font-size", `${STATE_NAMES.length/6 * 1.8}`);

  const chart = Object.assign(svg.node(), {
    update() {
        if (stackedStatus) {
          X = d3.map(areaData, x);
          Y = d3.map(areaData, y);
          Z = d3.map(areaData, z);

          xDomain = d3.extent(X);
          zDomain = Z;
          zDomain = new d3.InternSet(zDomain);

          I = d3.range(X.length).filter(i => zDomain.has(Z[i]));

          series = d3.stack()
              .keys(zDomain)
              .value(([x, I], z) => Y[I.get(z)])
              .order(order)
              .offset(offset)
            (d3.rollup(I, ([i]) => i, i => X[i], i => Z[i]))
            .map(s => s.map(d => Object.assign(d, {i: d.data[1].get(s.key)})));

          yDomain = d3.extent(series.flat(2));

          yScale = yType(yDomain, yRange);
          xScale = xType(xDomain, xRange);
          area = d3.area()
              .x(({i}) => xScale(X[i]))
              .y0(([y1]) => yScale(y1))
              .y1(([, y2]) => yScale(y2));

          color = d3.scaleOrdinal(zDomain, colors);

          xAxis = d3.axisBottom(xScale).ticks(width / 80, xFormat).tickSizeOuter(0);
          yAxis = d3.axisLeft(yScale).ticks(height / 50, yFormat);

          yAxisGroup.remove();
          xAxisGroup.remove();
          areaGroup.remove();

          areaGroup = svg.append("g")
            .selectAll("path")
            .data(series)
            .join("path")
              .attr("fill", ([{i}]) => color(Z[i]))
              .attr("d", area);

          areaGroup.append("title")
              .text(([{i}]) => Z[i]);

          yAxisGroup = svg.append("g")
              .attr("transform", `translate(${marginLeft},0)`)
              .call(yAxis)
              .call(g => g.select(".domain").remove())
              .call(g => g.selectAll(".tick line").clone()
                  .attr("x2", width - marginLeft - marginRight)
                  .attr("stroke-opacity", 0.1))

          if (areaGroup.size() !== 0) {
            xAxisGroup = svg.append("g")
                .attr("transform", `translate(0,${height - marginBottom})`)
                .call(xAxis);
          } else {
            xAxis = d3.axisBottom(xScale).ticks(0);
            xAxisGroup = svg.append("g")
                .attr("transform", `translate(0,${height - marginBottom})`)
                .call(xAxis);
          }
        } else {
          data = areaData.filter(d => d.state == selectedState);

          // Compute values.
          X = d3.map(data, x);
          Y = d3.map(data, y);
          I = d3.range(X.length);

          // Compute which data points are considered defined.
          const defined = (d, i) => !isNaN(X[i]) && !isNaN(Y[i]);
          const D = d3.map(data, defined);

          // Compute default domains.
          xDomain = d3.extent(X);
          yDomain = [0, d3.max(Y)];

          // Construct scales and axes.
          xScale = xType(xDomain, xRange);
          yScale = yType(yDomain, yRange);
          xAxis = d3.axisBottom(xScale).ticks(width / 80).tickSizeOuter(0);
          yAxis = d3.axisLeft(yScale).ticks(height / 40, yFormat);

          yAxisGroup.remove();
          xAxisGroup.remove();
          areaGroup.remove();

          area = d3.area()
              .defined(i => D[i])
              .curve(d3.curveLinear)
              .x(i => xScale(X[i]))
              .y0(yScale(0))
              .y1(i => yScale(Y[i]));

          yAxisGroup = svg.append("g")
              .attr("transform", `translate(${marginLeft},0)`)
              .call(yAxis)
              .call(g => g.select(".domain").remove())
              .call(g => g.selectAll(".tick line").clone()
                  .attr("x2", width - marginLeft - marginRight)
                  .attr("stroke-opacity", 0.1))
              .call(g => g.append("text")
                  .attr("x", -marginLeft)
                  .attr("y", 10)
                  .attr("fill", "currentColor")
                  .attr("text-anchor", "start")
                  .text(yLabel));

          areaGroup = svg.append("path")
              .attr("fill", color(selectedState))
              .attr("d", area(I));

          xAxisGroup = svg.append("g")
              .attr("transform", `translate(0,${height - marginBottom})`)
              .call(xAxis);
        }
      },
      swapGraph(state) {
        d3.selectAll('.legendItems')
          .select('text')
          .style('fill', 'white');

        if (stackedStatus || state != selectedState) {
          stackedStatus = false;
          selectedState = state;
        } else {
          stackedStatus = true;
          selectedState = 'none';
        }
      }
    }
  );

  return chart;
}

export var areaData = []

export function stackedLine() {

  return StackedAreaChart(areaData, {
    x: d => d.date,
    y: d => d.infected,
    z: d => d.state,
    height: 500
  })
}

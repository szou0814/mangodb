import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";

function StackedAreaChart(data, {
  x = ([x]) => x, // given d in data, returns the (ordinal) x-value
  y = ([, y]) => y, // given d in data, returns the (quantitative) y-value
  z = () => 1, // given d in data, returns the (categorical) z-value
  marginTop = 130, // top margin, in pixels
  marginRight = 30, // right margin, in pixels
  marginBottom = 30, // bottom margin, in pixels
  marginLeft = 40, // left margin, in pixels
  width = 740, // outer width, in pixels
  height = 400, // outer height, in pixels
  xType = d3.scaleUtc, // type of x-scale
  xDomain, // [xmin, xmax]
  xRange = [marginLeft, width - marginRight], // [left, right]
  yType = d3.scaleLinear, // type of y-scale
  yDomain = [0, 700000], // [ymin, ymax]
  yRange = [height - marginBottom, marginTop], // [bottom, top]
  zDomain, // array of z-values
  offset = d3.stackOffsetDiverging, // stack offset method
  order = d3.stackOrderNone, // stack order method
  xFormat, // a format specifier string for the x-axis
  yFormat, // a format specifier for the y-axis
  yLabel, // a label for the y-axis
  colors = d3.schemeTableau10, // array of colors for z
} = {}) {
  const STATE_NAMES = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri",
    "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
    "Wisconsin", "Wyoming"];

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
  const yScale = yType(yDomain, yRange);
  var color = d3.scaleOrdinal(zDomain, colors);

  var xAxis = d3.axisBottom(xScale).ticks(width / 80, xFormat).tickSizeOuter(0);
  const yAxis = d3.axisLeft(yScale).ticks(height / 50, yFormat);

  var area = d3.area()
      .x(({i}) => xScale(X[i]))
      .y0(([y1]) => yScale(y1))
      .y1(([, y2]) => yScale(y2));

  const svg = d3.create("svg")
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", [0, 0, width, height])
      .attr("style", "max-width: 100%; height: auto; height: intrinsic;");

  svg.append("g")
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

  return Object.assign(svg.node(), {
    update(date) {
      console.log(areaData);
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

        xScale = xType(xDomain, xRange);
        area = d3.area()
            .x(({i}) => xScale(X[i]))
            .y0(([y1]) => yScale(y1))
            .y1(([, y2]) => yScale(y2));

        color = d3.scaleOrdinal(zDomain, colors);

        xAxis = d3.axisBottom(xScale).ticks(width / 80, xFormat).tickSizeOuter(0);

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

        const size = zDomain.size/6 * 1.5
        svg.selectAll("legendSquares")
          .data(STATE_NAMES)
          .enter()
          .append("rect")
          .attr("x", function(d,i) { return (marginLeft-30) + (Math.floor(i/6) * (zDomain.size/6 * 10)) })
          .attr("y", function(d,i) { return Math.floor(i%6)*(size+5) })
          .attr("width", size)
          .attr("height", size)
          .style("fill", function(d) { return color(d) })

        svg.selectAll("legendLabels")
          .data(STATE_NAMES)
          .enter()
          .append("text")
          .attr("x", function(d,i) { return (marginLeft-30) + ((size*1.2) + (Math.floor(i/6) * (zDomain.size/6 * 10))) })
          .attr("y", function(d,i) { return Math.floor(i%6)*(size+5) + size/1.2 })
          .style("fill", 'white')
          .text(function(d) { return d })
          .attr("text-anchor", "left")
          .style("alignment-baseline", "middle")
          .style("font-size", `${zDomain.size/6}`)
      }
    }
  );
}

export var areaData = []

export function stackedLine() {
  // let data = [
  //   Object.assign({date: new Date('1962-04-01')}, {industry: "Wholesale and Retail Trade"}, {unemployed: 1000}),
  //   Object.assign({date: new Date('1962-04-01')}, {industry: "Manufacturing"}, {unemployed: 734}),
  //   Object.assign({date: new Date('1962-04-01')}, {industry: "Leisure and hospitality"}, {unemployed: 782}),
  //   Object.assign({date: new Date('1962-04-01')}, {industry: "Business services"}, {unemployed: 655}),
  //   Object.assign({date: new Date('1962-04-01')}, {industry: "Construction"}, {unemployed: 745}),
  //   Object.assign({date: new Date('1962-04-01')}, {industry: "Education and Health"}, {unemployed: 353}),
  //   Object.assign({date: new Date('1962-04-01')}, {industry: "Government"}, {unemployed: 430}),
  //   Object.assign({date: new Date('1962-04-01')}, {industry: "Finance"}, {unemployed: 228}),
  //   Object.assign({date: new Date('1962-04-01')}, {industry: "Self-employed"}, {unemployed: 239}),
  //   Object.assign({date: new Date('1962-04-01')}, {industry: "Other"}, {unemployed: 274}),
  //   Object.assign({date: new Date('1962-04-01')}, {industry: "Transportation and Utilities"}, {unemployed: 236}),
  //   Object.assign({date: new Date('1962-04-01')}, {industry: "Information"}, {unemployed: 125}),
  //   Object.assign({date: new Date('1962-04-01')}, {industry: "Agriculture"}, {unemployed: 154}),
  //   Object.assign({date: new Date('1962-04-01')}, {industry: "Mining and Extraction"}, {unemployed: 19}),
  //   Object.assign({date: new Date('1962-05-01')}, {industry: "Wholesale and Retail Trade"}, {unemployed: 1023}),
  //   Object.assign({date: new Date('1962-05-01')}, {industry: "Manufacturing"}, {unemployed: 694}),
  //   Object.assign({date: new Date('1962-05-01')}, {industry: "Leisure and hospitality"}, {unemployed: 779}),
  //   Object.assign({date: new Date('1962-05-01')}, {industry: "Business services"}, {unemployed: 587}),
  //   Object.assign({date: new Date('1962-05-01')}, {industry: "Construction"}, {unemployed: 812}),
  //   Object.assign({date: new Date('1962-05-01')}, {industry: "Education and Health"}, {unemployed: 349}),
  //   Object.assign({date: new Date('1962-05-01')}, {industry: "Government"}, {unemployed: 409}),
  //   Object.assign({date: new Date('1962-05-01')}, {industry: "Finance"}, {unemployed: 240}),
  //   Object.assign({date: new Date('1962-05-01')}, {industry: "Self-employed"}, {unemployed: 262}),
  //   Object.assign({date: new Date('1962-05-01')}, {industry: "Other"}, {unemployed: 232}),
  //   Object.assign({date: new Date('1962-05-01')}, {industry: "Transportation and Utilities"}, {unemployed: 223}),
  //   Object.assign({date: new Date('1962-05-01')}, {industry: "Information"}, {unemployed: 112}),
  //   Object.assign({date: new Date('1962-05-01')}, {industry: "Agriculture"}, {unemployed: 173}),
  //   Object.assign({date: new Date('1962-05-01')}, {industry: "Mining and Extraction"}, {unemployed: 25}),
  //   Object.assign({date: new Date('1972-10-01')}, {industry: "Wholesale and Retail Trade"}, {unemployed: 983}),
  //   Object.assign({date: new Date('1972-10-01')}, {industry: "Manufacturing"}, {unemployed: 739}),
  //   Object.assign({date: new Date('1972-10-01')}, {industry: "Leisure and hospitality"}, {unemployed: 789}),
  //   Object.assign({date: new Date('1972-10-01')}, {industry: "Business services"}, {unemployed: 623}),
  //   Object.assign({date: new Date('1972-10-01')}, {industry: "Construction"}, {unemployed: 669}),
  //   Object.assign({date: new Date('1972-10-01')}, {industry: "Education and Health"}, {unemployed: 381}),
  //   Object.assign({date: new Date('1972-10-01')}, {industry: "Government"}, {unemployed: 311}),
  //   Object.assign({date: new Date('1972-10-01')}, {industry: "Finance"}, {unemployed: 226}),
  //   Object.assign({date: new Date('1972-10-01')}, {industry: "Self-employed"}, {unemployed: 213}),
  //   Object.assign({date: new Date('1972-10-01')}, {industry: "Other"}, {unemployed: 247}),
  //   Object.assign({date: new Date('1972-10-01')}, {industry: "Transportation and Utilities"}, {unemployed: 192}),
  //   Object.assign({date: new Date('1972-10-01')}, {industry: "Information"}, {unemployed: 140}),
  //   Object.assign({date: new Date('1972-10-01')}, {industry: "Agriculture"}, {unemployed: 173}),
  //   Object.assign({date: new Date('1972-10-01')}, {industry: "Mining and Extraction"}, {unemployed: 25}),
  // ]

  return StackedAreaChart(areaData, {
    x: d => d.date,
    y: d => d.infected,
    z: d => d.state,
    height: 500
  })
}

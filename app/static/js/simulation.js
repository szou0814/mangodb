import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import * as topojson from "https://cdn.jsdelivr.net/npm/topojson-client@3/+esm";
// import {Scrubber} from "@mbostock/scrubber";

export async function chart() {
  const us = await d3.json("https://cdn.jsdelivr.net/npm/us-atlas@1/us/10m.json");

  us.objects.lower48 = { // pulls the geometries of each state for later use
    type: "GeometryCollection",
    geometries: us.objects.states.geometries.filter(d => d.id !== "02" && d.id !== "15")
  };

  // INITIALIZES THE SVG
  const svg = d3.create("svg")
      .attr("viewBox", [0, 0, 960, 600]); // sizes the SVG

  // creates the us
  svg.append("path")
      .datum(topojson.merge(us, us.objects.lower48.geometries))
      .attr("fill", "#ddd")
      .attr("d", d3.geoPath());

  // creates the borders
  svg.append("path")
      .datum(topojson.mesh(us, us.objects.lower48, (a, b) => a !== b))
      .attr("fill", "none")
      .attr("stroke", "white")
      .attr("stroke-linejoin", "round")
      .attr("d", d3.geoPath());

  // creates a container that will group the dots that aren't the main blue dot
  const g = svg.append("g")
      .attr("fill", "none") // sets the fill of these dots
      .attr("stroke", "black"); // sets the outline of these dots

  const dot = g.selectAll("circle") // selects all cuurent and new circle elements inside g
    .data(data) // binds this to data array
    .join("circle") // binds and creates a circle DOM element to each new data point
      .attr("transform", d => `translate(${d})`); // transforms and translates each dot to their [x,y] coordinate
        // the d essentially just comes from data and is whatever object thing that was appended there

  // creates main blue dot
  svg.append("circle")
      .attr("fill", "blue")
      .attr("transform", `translate(${data[0]})`)
      .attr("r", 3);

  let previousDate = -Infinity;

  return Object.assign(svg.node(), {
    update(date) {
      dot // enters the dots and does the little animation
        .filter(d => d.date > previousDate && d.date <= date)
        .transition().attr("r", 3);
      dot // exits the dots + animation
        .filter(d => d.date <= previousDate && d.date > date)
        .transition().attr("r", 0);
      previousDate = date;
    }
  });
}

const data = [
  Object.assign([523.3754804030681, 353.07903336329866], {date: new Date("1962-07-01")}),
  Object.assign([544.5356591678276, 355.4857849174865], {date: new Date("1964-08-01")}),
  Object.assign([516.9205616647201, 356.6437794871256], {date: new Date("1965-08-01")}),
  Object.assign([558.10081249479, 386.8683472613426], {date: new Date("1967-10-01")}),
  Object.assign([549.6127467643465, 379.4879303612154], {date: new Date("1967-10-01")}),
  Object.assign([603.9256664458603, 337.49296790198935], {date: new Date("1968-03-01")}),
  Object.assign([553.2567848000133, 349.56052772921134], {date: new Date("1968-03-01")}),
  Object.assign([508.70236432204763, 363.29757342091443], {date: new Date("1968-07-01")}),
  Object.assign([497.36133135143217, 353.5816462932148], {date: new Date("1968-07-01")}),
  Object.assign([520.1560720060365, 334.9167421877769], {date: new Date("1968-11-01")}),
  Object.assign([549.0293044955295, 322.4940372243286], {date: new Date("1969-04-01")}),
  Object.assign([520.0009258632932, 372.62839130543307], {date: new Date("1969-04-01")}),
  Object.assign([563.7512736801056, 342.92601346652805], {date: new Date("1969-05-01")}),
  Object.assign([518.7902757866219, 341.71822438114646], {date: new Date("1969-05-01")}),
  Object.assign([576.391869431155, 365.29985641776386], {date: new Date("1969-11-01")}),
  Object.assign([557.6727608570873, 318.3752859090938], {date: new Date("1970-03-01")}),
  Object.assign([529.39448445367, 307.1011849708477], {date: new Date("1970-10-01")}),
  Object.assign([502.5047165315647, 353.98738527064006], {date: new Date("1970-10-01")}),
  Object.assign([563.7584451355674, 437.8400597753878], {date: new Date("1970-11-01")}),
  Object.assign([508.94904031862677, 285.9435928657131], {date: new Date("1970-11-01")}),
  Object.assign([560.9353261122661, 287.8835037926367], {date: new Date("1971-02-01")}),
  Object.assign([568.3623235711143, 322.20575691286194], {date: new Date("1971-02-01")})
]

// data = (await FileAttachment("walmart.tsv").tsv())
//   .map(d => {
//     const p = projection(d);
//     p.date = parseDate(d.date);
//     return p;
//   })
//   .sort((a, b) => a.date - b.date)
//
// parseDate = d3.utcParse("%m/%d/%Y")
// projection = d3.geoAlbersUsa().scale(1280).translate([480, 300])
//

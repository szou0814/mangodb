import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import * as topojson from "https://cdn.jsdelivr.net/npm/topojson-client@3/+esm";

export async function map() {
  const us = await d3.json("https://cdn.jsdelivr.net/npm/us-atlas@1/us/10m.json");
  const stateFeatures = topojson.feature(us, us.objects.states).features;
  const states = [
    { name: "Alabama", id: "01" }, { name: "Alaska", id: "02" }, { name: "Arizona", id: "04" },
    { name: "Arkansas", id: "05" }, { name: "California", id: "06" }, { name: "Colorado", id: "08" },
    { name: "Connecticut", id: "09" }, { name: "Delaware", id: "10" }, { name: "District of Columbia", id: "11" },
    { name: "Florida", id: "12" }, { name: "Georgia", id: "13" }, { name: "Hawaii", id: "15" },
    { name: "Idaho", id: "16" }, { name: "Illinois", id: "17" }, { name: "Indiana", id: "18" },
    { name: "Iowa", id: "19" }, { name: "Kansas", id: "20" }, { name: "Kentucky", id: "21" },
    { name: "Louisiana", id: "22" }, { name: "Maine", id: "23" }, { name: "Maryland", id: "24" },
    { name: "Massachusetts", id: "25" }, { name: "Michigan", id: "26" }, { name: "Minnesota", id: "27" },
    { name: "Mississippi", id: "28" }, { name: "Missouri", id: "29" }, { name: "Montana", id: "30" },
    { name: "Nebraska", id: "31" }, { name: "Nevada", id: "32" }, { name: "New Hampshire", id: "33" },
    { name: "New Jersey", id: "34" }, { name: "New Mexico", id: "35" }, { name: "New York", id: "36" },
    { name: "North Carolina", id: "37" }, { name: "North Dakota", id: "38" }, { name: "Ohio", id: "39" },
    { name: "Oklahoma", id: "40" }, { name: "Oregon", id: "41" }, { name: "Pennsylvania", id: "42" },
    { name: "Rhode Island", id: "44" }, { name: "South Carolina", id: "45" }, { name: "South Dakota", id: "46" },
    { name: "Tennessee", id: "47" }, { name: "Texas", id: "48" }, { name: "Utah", id: "49" },
    { name: "Vermont", id: "50" }, { name: "Virginia", id: "51" }, { name: "Washington", id: "53" },
    { name: "West Virginia", id: "54" }, { name: "Wisconsin", id: "55" }, { name: "Wyoming", id: "56" }
  ];
  let points = [];
  let prevPoints = null;

  //i took this from walmart growth code except changed it to fitsize so it automatically scales and centers svg map
  //dis is called a projection or smth
  //it converts our lat long into pixel coordinates on the svg
  //MUST HAVE THIS SO DO NOT CHANGE (unless u find bug ofc hehe)
  const projection = d3.geoAlbers().fitSize([960, 600], topojson.feature(us, us.objects.states));

  function createPoint(state_id) {
    const id = states.find(i => i.name === state_id).id;
    const feature = stateFeatures.find(d => d.id === id);
    let point;

    while (true) {
      //d3.geoBounds gives like a box surrounding the state
      const bounds = d3.geoBounds(feature);
      const x = bounds[0][0] + Math.random() * (bounds[1][0] - bounds[0][0]);
      const y = bounds[0][1] + Math.random() * (bounds[1][1] - bounds[0][1]);

      point = [x,y];
      //so dis is to check if its actually in the state
      if (d3.geoContains(feature, [x,y])) {
        break;
      }
    }

    return projection(point);
  }

  us.objects.states = { // pulls the geometries of each state for later use
    type: "GeometryCollection",
    geometries: us.objects.states.geometries
  };

  // INITIALIZES THE SVG
  const svg = d3.create("svg")
      .attr("viewBox", [0, 0, 960, 600]); // sizes view box

  // creates the us
  svg.append("path")
      .datum(topojson.merge(us, us.objects.states.geometries))
      .attr("fill", "#ddd")
      .attr("d", d3.geoPath());

  // creates the borders
  svg.append("path")
      .datum(topojson.mesh(us, us.objects.states, (a, b) => a !== b))
      .attr("fill", "none")
      .attr("stroke", "white")
      .attr("stroke-linejoin", "round")
      .attr("d", d3.geoPath());

  // creates a container that will group the dots that aren't the main blue dot
  const g = svg.append("g")
      .attr("fill", "none") // sets the fill of these dots
      .attr("stroke", "black"); // sets the outline of these dots

  const dot = g.selectAll("circle") // selects all cuurent and new circle elements inside g
    .data(mapData) // binds this to data array
    .join("circle") // binds and creates a circle DOM element to each new data point
      .attr("transform", d => `translate(${d})`); // transforms and translates each dot to their [x,y] coordinate
        // the d essentially just comes from data and is whatever object thing that was appended there

  let previousDate = -Infinity;

  return Object.assign(svg.node(), {
    update(date) {
      const circles = g.selectAll("circle")
        .data(mapData);

      circles
        .enter()
        .filter(d => d.date > previousDate && d.date <= date)
        .append("circle")
        .attr("r", 0)
        .attr("transform", d => `translate(${d[0]},${d[1]})`)
        .merge(circles)
        .transition()
        .attr("r", 3);

      previousDate = date;
    },
    createPoint
  });
}

export const mapData = []

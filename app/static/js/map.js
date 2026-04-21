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
      dot // enters the dots and does the little animation
        .filter(d => d.date > previousDate && d.date <= date)
        .transition().attr("r", 3);
      dot // exits the dots + animation
        .filter(d => d.date <= previousDate && d.date > date)
        .transition().attr("r", 0);
      previousDate = date;
    },
    createPoint
  });
}

export const mapData = []
// export const data = [
//   Object.assign([523.3754804030681, 353.07903336329866], {date: new Date("1962-07-01")}),
//   Object.assign([544.5356591678276, 355.4857849174865], {date: new Date("1964-08-01")}),
//   Object.assign([516.9205616647201, 356.6437794871256], {date: new Date("1965-08-01")}),
//   Object.assign([558.10081249479, 386.8683472613426], {date: new Date("1967-10-01")}),
//   Object.assign([549.6127467643465, 379.4879303612154], {date: new Date("1967-10-01")}),
//   Object.assign([603.9256664458603, 337.49296790198935], {date: new Date("1968-03-01")}),
//   Object.assign([553.2567848000133, 349.56052772921134], {date: new Date("1968-03-01")}),
//   Object.assign([508.70236432204763, 363.29757342091443], {date: new Date("1968-07-01")}),
//   Object.assign([497.36133135143217, 353.5816462932148], {date: new Date("1968-07-01")}),
//   Object.assign([520.1560720060365, 334.9167421877769], {date: new Date("1968-11-01")}),
//   Object.assign([549.0293044955295, 322.4940372243286], {date: new Date("1969-04-01")}),
//   Object.assign([520.0009258632932, 372.62839130543307], {date: new Date("1969-04-01")}),
//   Object.assign([563.7512736801056, 342.92601346652805], {date: new Date("1969-05-01")}),
//   Object.assign([518.7902757866219, 341.71822438114646], {date: new Date("1969-05-01")}),
//   Object.assign([576.391869431155, 365.29985641776386], {date: new Date("1969-11-01")}),
//   Object.assign([557.6727608570873, 318.3752859090938], {date: new Date("1970-03-01")}),
//   Object.assign([529.39448445367, 307.1011849708477], {date: new Date("1970-10-01")}),
//   Object.assign([502.5047165315647, 353.98738527064006], {date: new Date("1970-10-01")}),
//   Object.assign([563.7584451355674, 437.8400597753878], {date: new Date("1970-11-01")}),
//   Object.assign([508.94904031862677, 285.9435928657131], {date: new Date("1970-11-01")}),
//   Object.assign([560.9353261122661, 287.8835037926367], {date: new Date("1971-02-01")}),
//   Object.assign([568.3623235711143, 322.20575691286194], {date: new Date("1971-02-01")}),
//   Object.assign([517.2318591468219, 336.4973030774604], {date: new Date("1972-05-01")}),
//   Object.assign([523.5278497867812, 356.8397587506481], {date: new Date("1972-06-01")}),
//   Object.assign([511.7850701865399, 373.22477082000705], {date: new Date("1972-07-01")}),
//   Object.assign([543.5115770317782, 394.0802238597223], {date: new Date("1972-07-01")}),
//   Object.assign([585.7119954223638, 362.29945716669704], {date: new Date("1972-08-01")}),
//   Object.assign([535.9871960967822, 324.34369203693336], {date: new Date("1972-08-01")}),
//   Object.assign([499.3650140301644, 405.7298458295761], {date: new Date("1972-10-01")}),
//   Object.assign([528.3473347962284, 379.85871172766815], {date: new Date("1972-10-01")}),
//   Object.assign([580.273433430591, 356.8678412621057], {date: new Date("1972-10-01")}),
//   Object.assign([526.6608110082664, 339.88792387192655], {date: new Date("1972-11-01")}),
//   Object.assign([529.3848365069086, 297.78304537771953], {date: new Date("1972-11-01")}),
//   Object.assign([600.4108169625575, 358.9894471920345], {date: new Date("1972-11-01")}),
//   Object.assign([496.6655232216779, 337.62061508150646], {date: new Date("1973-02-01")}),
//   Object.assign([611.9552684886062, 365.7974025941612], {date: new Date("1973-02-01")}),
//   Object.assign([560.2169641922967, 294.84179681088585], {date: new Date("1973-05-01")}),
//   Object.assign([542.6582095144265, 376.4108259487173], {date: new Date("1973-05-01")}),
//   Object.assign([553.4335495541601, 293.4521677162222], {date: new Date("1973-06-01")}),
//   Object.assign([514.886383359566, 364.8791272716942], {date: new Date("1973-06-01")}),
//   Object.assign([522.7259888011041, 392.4924103881874], {date: new Date("1973-07-01")}),
//   Object.assign([574.4809811753578, 308.69090341088247], {date: new Date("1973-07-03")}),
// ]

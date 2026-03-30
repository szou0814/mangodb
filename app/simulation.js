import {Scrubber} from "@mbostock/scrubber"

chart = {
  const svg = d3.create("svg")
      .attr("viewBox", [0, 0, 960, 600]);

  svg.append("path")
      .datum(topojson.merge(us, us.objects.lower48.geometries))
      .attr("fill", "#ddd")
      .attr("d", d3.geoPath());

  svg.append("path")
      .datum(topojson.mesh(us, us.objects.lower48, (a, b) => a !== b))
      .attr("fill", "none")
      .attr("stroke", "white")
      .attr("stroke-linejoin", "round")
      .attr("d", d3.geoPath());

  const g = svg.append("g")
      .attr("fill", "none")
      .attr("stroke", "black");

  const dot = g.selectAll("circle")
    .data(data)
    .join("circle")
      .attr("transform", d => `translate(${d})`);

  svg.append("circle")
      .attr("fill", "blue")
      .attr("transform", `translate(${data[0]})`)
      .attr("r", 3);

  let previousDate = -Infinity;

  return Object.assign(svg.node(), {
    update(date) {
      dot // enter
        .filter(d => d.date > previousDate && d.date <= date)
        .transition().attr("r", 3);
      dot // exit
        .filter(d => d.date <= previousDate && d.date > date)
        .transition().attr("r", 0);
      previousDate = date;
    }
  });
}

update = chart.update(date)

data =
  Array(21) [
  Array(2) [523.3754804030681, 353.07903336329866, date: 1962-07-01],
  Array(2) [544.5356591678276, 355.4857849174865, date: 1964-08-01],
  Array(2) [516.9205616647201, 356.6437794871256, date: 1965-08-01],
  Array(2) [558.10081249479, 386.8683472613426, date: 1967-10-01],
  Array(2) [549.6127467643465, 379.4879303612154, date: 1967-10-01],
  Array(2) [603.9256664458603, 337.49296790198935, date: 1968-03-01],
  Array(2) [553.2567848000133, 349.56052772921134, date: 1968-03-01],
  Array(2) [508.70236432204763, 363.29757342091443, date: 1968-07-01],
  Array(2) [497.36133135143217, 353.5816462932148, date: 1968-07-01],
  Array(2) [520.1560720060365, 334.9167421877769, date: 1968-11-01],
  Array(2) [549.0293044955295, 322.4940372243286, date: 1969-04-01],
  Array(2) [520.0009258632932, 372.62839130543307, date: 1969-04-01],
  Array(2) [563.7512736801056, 342.92601346652805, date: 1969-05-01],
  Array(2) [518.7902757866219, 341.71822438114646, date: 1969-05-01],
  Array(2) [576.391869431155, 365.29985641776386, date: 1969-11-01],
  Array(2) [557.6727608570873, 318.3752859090938, date: 1970-03-01],
  Array(2) [529.39448445367, 307.1011849708477, date: 1970-10-01],
  Array(2) [502.5047165315647, 353.98738527064006, date: 1970-10-01],
  Array(2) [563.7584451355674, 437.8400597753878, date: 1970-11-01],
  Array(2) [508.94904031862677, 285.9435928657131, date: 1970-11-01],
  Array(2) [560.9353261122661, 287.8835037926367, date: 1971-02-01],
  Array(2) [568.3623235711143, 322.20575691286194, date: 1971-02-01]
]

// data = (await FileAttachment("walmart.tsv").tsv())
//   .map(d => {
//     const p = projection(d);
//     p.date = parseDate(d.date);
//     return p;
//   })
//   .sort((a, b) => a.date - b.date)

parseDate = d3.utcParse("%m/%d/%Y")
projection = d3.geoAlbersUsa().scale(1280).translate([480, 300])

us = {
  const us = await d3.json("https://cdn.jsdelivr.net/npm/us-atlas@1/us/10m.json");
  us.objects.lower48 = {
    type: "GeometryCollection",
    geometries: us.objects.states.geometries.filter(d => d.id !== "02" && d.id !== "15")
  };
  return us;
}

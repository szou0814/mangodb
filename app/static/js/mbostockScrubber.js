export function Scrubber(values, {
  format = value => value,
  initial = 0,
  direction = 1,
  delay = null,
  autoplay = true,
  loop = true,
  loopDelay = null,
  alternate = false
} = {}) {
  values = Array.from(values);
  const cont = document.createElement('div');

  const form = document.createElement('form');
  form.style = "font: 12px var(--sans-serif); font-variant-numeric: tabular-nums; display: flex; height: 33px; align-items: center;"

  const b = document.createElement('button');
  b.name = 'b';
  b.type = 'button';
  b.style = 'margin-right: 0.4em; width: 5em;';

  const label = document.createElement('label');
  label.style = 'display: flex; align-items: center;'

  const i = document.createElement('input');
  i.name = 'i';
  i.type = 'range';
  i.min = 0;
  i.max = values.length - 1 ;
  i.value = initial;
  i.step = 1;
  i.style = 'width: 180px;';

  const o = document.createElement('output');
  o.name = 'o';
  o.style = "margin-left: 0.4em;";

  label.append(i, o);
  form.append(b, label);
  cont.append(form);

  let frame = null;
  let timer = null;
  let interval = null;

  function start() {
    form.b.textContent = "Pause";
    if (delay === null) frame = requestAnimationFrame(tick);
    else interval = setInterval(tick, delay);
  }

  function stop() {
    form.b.textContent = "Play";
    if (frame !== null) cancelAnimationFrame(frame), frame = null;
    if (timer !== null) clearTimeout(timer), timer = null;
    if (interval !== null) clearInterval(interval), interval = null;
  }

  function running() {
    return frame !== null || timer !== null || interval !== null;
  }

  function tick() {
    if (form.i.valueAsNumber === (direction > 0 ? values.length - 1 : direction < 0 ? 0 : NaN)) {
      if (!loop) return stop();
      if (alternate) direction = -direction;
      if (loopDelay !== null) {
        if (frame !== null) cancelAnimationFrame(frame), frame = null;
        if (interval !== null) clearInterval(interval), interval = null;
        timer = setTimeout(() => (step(), start()), loopDelay);
        return;
      }
    }
    if (delay === null) frame = requestAnimationFrame(tick);
    step();
  }

  function step() {
    form.i.valueAsNumber = (form.i.valueAsNumber + direction + values.length) % values.length;
    form.i.dispatchEvent(new CustomEvent("input", {bubbles: true}));
  }

  form.i.oninput = event => {
    if (event && event.isTrusted && running()) stop();
    form.value = values[form.i.valueAsNumber];
    let date = form.value;
    form.o.value = format(`${date.toLocaleString('default', {month: 'short'})} ${date.getDate()} ${date.getFullYear()}`, form.i.valueAsNumber, values);
  };

  form.b.onclick = () => {
    if (running()) return stop();
    direction = alternate && form.i.valueAsNumber === values.length - 1 ? -1 : 1;
    form.i.valueAsNumber = (form.i.valueAsNumber + direction) % values.length;
    form.i.dispatchEvent(new CustomEvent("input", {bubbles: true}));
    start();
  };

  form.i.oninput();

  if (autoplay) start();
  else stop();

  // Inputs.disposal(form).then(stop);
  return form;
}

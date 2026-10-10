"use strict";

const state = { config: null, alternatives: [], result: null, scenario: null, unit: "years", chartType: "trajectory", barUnit: "percent", pendingDefaults: 0 };
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const numberFields = ["mileage", "energyMix", "secondHandCarMileage", "secondHandCarAge", "meanConsumptionLiter", "meanConsumptionWh", "drivingShare", "massValue", "carProductionFootprint", "WTT", "TTW", "batteryCapacity", "batteryProductionFootprint", "batteryLifeTime"];
const fieldDefinitions = [
  ["meanConsumptionLiter", "Fuel consumption", "l / 100 km"],
  ["meanConsumptionWh", "Electric consumption", "kWh / 100 km"],
  ["drivingShare", "Electric driving share", "0–1"],
  ["massValue", "Vehicle mass", "kg"],
  ["carProductionFootprint", "Production + EoL footprint", "kgCO₂ / kg"],
  ["WTT", "Well-to-tank footprint", "gCO₂ / l"],
  ["TTW", "Tank-to-wheel footprint", "gCO₂ / l"],
  ["batteryCapacity", "Battery capacity", "kWh"],
  ["batteryProductionFootprint", "Battery production footprint", "kgCO₂ / kWh"],
  ["batteryLifeTime", "Battery lifetime", "km"],
];

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, char => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"})[char]);
}

function options(items, selected) {
  return items.map(item => `<option value="${escapeHtml(item)}" ${item === selected ? "selected" : ""}>${escapeHtml(item)}</option>`).join("");
}

function numericField(key, label, unit, value, required = false) {
  const tip = state.config.tooltips[key] || "";
  return `<label class="field" data-row="${key}" title="${escapeHtml(tip)}"><span>${label} <small>${unit}</small></span><input data-field="${key}" type="number" min="0" step="any" ${required ? "required" : ""} value="${value ?? ""}"></label>`;
}

function vehicleMarkup(vehicle, index, current) {
  const title = current ? "Current vehicle" : `Replacement ${index + 1}`;
  return `<div class="vehicle-form" data-vehicle="${current ? "current" : index}">
    ${!current ? `<div class="replacement-top"><span class="replacement-badge">OPTION ${String(index + 1).padStart(2, "0")}</span><button class="remove-car" type="button" aria-label="Remove replacement ${index + 1}">Remove ×</button></div>` : ""}
    <div class="field-grid"><label class="field"><span>Vehicle segment</span><select data-field="carSegment">${options(state.config.segments, vehicle.carSegment)}</select></label><label class="field"><span>Powertrain</span><select data-field="engineType">${options(state.config.engines, vehicle.engineType)}</select></label></div>
    ${current ? `<div class="field-grid"><label class="field"><span>Current mileage <small>km</small></span><input data-field="mileage" type="number" min="0" step="any" required value="${vehicle.mileage ?? ""}" placeholder="e.g. 80,000"></label><label class="field"><span>Country</span><select data-field="country">${options(state.config.countries, vehicle.country)}</select></label></div>${numericField("energyMix", "Electricity mix", "gCO₂ / kWh", vehicle.energyMix, true)}` : ""}
    <details class="advanced vehicle-advanced"><summary>Advanced vehicle inputs <span>⌄</span></summary><div class="advanced-body"><label class="check-field"><input data-field="secondHandCar" type="checkbox" ${vehicle.secondHandCar ? "checked" : ""}><span>Purchased second hand</span></label><div class="field-grid secondhand-fields">${numericField("secondHandCarMileage", "Mileage when purchased", "km", vehicle.secondHandCarMileage)}${numericField("secondHandCarAge", "Age when purchased", "years", vehicle.secondHandCarAge)}</div><div class="field-grid technical-fields">${fieldDefinitions.map(([key, label, unit]) => numericField(key, label, unit, vehicle[key])).join("")}</div><button type="button" class="reset-vehicle">Reset technical inputs to workbook defaults</button></div></details>
  </div>`;
}

function readVehicle(form, current) {
  const vehicle = {};
  for (const input of $$('[data-field]', form)) {
    const key = input.dataset.field;
    if (input.type === "checkbox") vehicle[key] = input.checked;
    else if (numberFields.includes(key)) vehicle[key] = input.value.trim() === "" ? null : Number(input.value);
    else vehicle[key] = input.value;
  }
  if (!vehicle.secondHandCar) {
    vehicle.secondHandCarMileage = null;
    vehicle.secondHandCarAge = null;
  }
  if (!current) {
    delete vehicle.country;
    delete vehicle.energyMix;
    delete vehicle.mileage;
  }
  return vehicle;
}

function renderVehicles() {
  const current = state.current || state.config.defaults.current;
  $("#current-form").innerHTML = vehicleMarkup(current, 0, true);
  $("#alternatives").innerHTML = state.alternatives.map((car, index) => `<section class="panel replacement-panel">${vehicleMarkup(car, index, false)}</section>`).join("");
  $$(".vehicle-form").forEach(setVehicleVisibility);
  $$(".remove-car").forEach((button, index) => { button.disabled = state.alternatives.length === 1; button.addEventListener("click", () => {
    storeVehicleForms();
    state.alternatives.splice(index, 1);
    renderVehicles();
    invalidateResults();
  }); });
}

function storeVehicleForms() {
  state.current = readVehicle($("#current-form .vehicle-form"), true);
  state.alternatives = $$("#alternatives .vehicle-form").map(form => readVehicle(form, false));
}

function setVehicleVisibility(form) {
  const engine = $('[data-field="engineType"]', form).value;
  const used = $('[data-field="secondHandCar"]', form).checked;
  $(".secondhand-fields", form).classList.toggle("hidden", !used);
  const fuel = engine !== "BEV";
  const electric = engine === "BEV" || engine === "Plug-in Hybrid";
  for (const key of ["meanConsumptionLiter", "WTT", "TTW"]) setRow(form, key, fuel);
  setRow(form, "meanConsumptionWh", electric);
  setRow(form, "drivingShare", engine === "Plug-in Hybrid");
  for (const key of ["batteryCapacity", "batteryProductionFootprint", "batteryLifeTime"]) setRow(form, key, engine === "BEV");
  const country = $('[data-field="country"]', form);
  if (country) $('[data-field="energyMix"]', form).readOnly = country.value !== "Custom";
}

function setRow(form, key, visible) {
  const row = $(`[data-row="${key}"]`, form);
  row.classList.toggle("hidden", !visible);
  $('[data-field]', row).required = visible;
}

async function request(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail = body.detail;
    throw new Error(Array.isArray(detail) ? detail.map(item => `${item.loc?.slice(-1)[0] ?? "Input"}: ${item.msg}`).join(" · ") : detail || `Request failed (${response.status})`);
  }
  return response;
}

async function updateDefaults(form, resetAll = false) {
  invalidateResults();
  const segment = $('[data-field="carSegment"]', form).value;
  const engine = $('[data-field="engineType"]', form).value;
  const sequence = Number(form.dataset.defaultsSequence || 0) + 1;
  form.dataset.defaultsSequence = String(sequence);
  state.pendingDefaults += 1;
  $("#compute").disabled = true;
  try {
    const response = await request(`/api/vehicle-defaults?segment=${encodeURIComponent(segment)}&engine=${encodeURIComponent(engine)}`);
    const defaults = await response.json();
    if (!form.isConnected || Number(form.dataset.defaultsSequence) !== sequence) return;
    if ($('[data-field="carSegment"]', form).value !== segment || $('[data-field="engineType"]', form).value !== engine) return;
    for (const [key] of fieldDefinitions) $(`[data-field="${key}"]`, form).value = defaults[key] ?? "";
    if (engine === "BEV") $('[data-field="batteryLifeTime"]', form).value = $("#bev-lifespan").value;
    if (resetAll) {
      $('[data-field="secondHandCar"]', form).checked = false;
      for (const key of ["secondHandCarMileage", "secondHandCarAge"]) $(`[data-field="${key}"]`, form).value = "";
    }
    setVehicleVisibility(form);
  } catch (error) { showError(error.message); }
  finally {
    state.pendingDefaults -= 1;
    if (state.pendingDefaults === 0) $("#compute").disabled = false;
  }
}

function scenarioFromForms() {
  const current = readVehicle($("#current-form .vehicle-form"), true);
  const alternatives = $$("#alternatives .vehicle-form").map(form => readVehicle(form, false));
  const keepEOL = $("#keep-eol").checked;
  const settings = {
    ICElifeSpan: Number($("#ice-lifespan").value),
    BEVlifeSpan: Number($("#bev-lifespan").value),
    km2yearsConvFactor: Number($("#annual-mileage").value),
    maintenance: $("#maintenance").value === "true",
    keepEOL,
    keepLifeSpan: keepEOL ? null : Number($("#keep-lifespan").value),
    keepUnits: $("#keep-units").value,
  };
  return { current, alternatives, settings };
}

function showError(message) {
  const error = $("#error");
  error.textContent = message;
  error.classList.toggle("hidden", !message);
}

function selectConfigTab(name) {
  $$("[data-config-tab]").forEach(button => {
    const active = button.dataset.configTab === name;
    button.classList.toggle("selected", active);
    button.setAttribute("aria-selected", String(active));
  });
  $$("[data-config-panel]").forEach(panel => panel.classList.toggle("hidden", panel.dataset.configPanel !== name));
  $(".setup-hint").textContent = `${String(["current", "alternatives", "settings"].indexOf(name) + 1).padStart(2, "0")} / 03`;
  $(".config-content").scrollTop = 0;
}

function selectView(name) {
  $(".workspace").dataset.view = name;
  $$("[data-view]").forEach(button => {
    const active = button.dataset.view === name;
    button.classList.toggle("selected", active);
    button.setAttribute("aria-pressed", String(active));
  });
  if (name === "results" && $("#chart").classList.contains("js-plotly-plot")) {
    requestAnimationFrame(() => window.Plotly.Plots.resize($("#chart")));
  }
  requestAnimationFrame(syncSplitters);
}

const splitPreferences = {setup: null, table: null};
let plotResizeFrame = 0;

function clamp(value, minimum, maximum) {
  return Math.min(Math.max(value, minimum), maximum);
}

function schedulePlotResize() {
  if (plotResizeFrame) return;
  plotResizeFrame = requestAnimationFrame(() => {
    plotResizeFrame = 0;
    const chart = $("#chart");
    if (window.Plotly && chart.classList.contains("js-plotly-plot") && chart.offsetWidth) window.Plotly.Plots.resize(chart);
  });
}

function setupAvailableWidth() {
  const workspace = $(".workspace");
  const style = getComputedStyle(workspace);
  return workspace.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight) - $("#workspace-splitter").offsetWidth;
}

function setupLimits() {
  const available = setupAvailableWidth();
  return {minimum: 250, maximum: Math.max(250, Math.min(760, available - 340))};
}

function setSetupWidth(width) {
  if (matchMedia("(max-width: 700px)").matches) return;
  const {minimum, maximum} = setupLimits();
  const value = clamp(width, minimum, maximum);
  $(".workspace").style.setProperty("--setup-width", `${value}px`);
  const divider = $("#workspace-splitter");
  divider.setAttribute("aria-valuemin", String(minimum));
  divider.setAttribute("aria-valuemax", String(maximum));
  divider.setAttribute("aria-valuenow", String(Math.round(value)));
  schedulePlotResize();
}

function tableLimits() {
  const results = $(".results-column");
  const head = $(".results-head");
  const headMargin = parseFloat(getComputedStyle(head).marginBottom) || 0;
  const chartMinimum = matchMedia("(max-width: 700px), (max-height: 700px)").matches ? 75 : 100;
  const maximum = Math.max(120, results.clientHeight - head.offsetHeight - headMargin - $("#results-splitter").offsetHeight - chartMinimum);
  return {minimum: Math.min(120, maximum), maximum};
}

function setTableHeight(height) {
  const {minimum, maximum} = tableLimits();
  const value = clamp(height, minimum, maximum);
  const results = $(".results-column");
  results.style.setProperty("--table-height", `${value}px`);
  results.classList.add("table-resized");
  const divider = $("#results-splitter");
  divider.setAttribute("aria-valuemin", String(minimum));
  divider.setAttribute("aria-valuemax", String(maximum));
  divider.setAttribute("aria-valuenow", String(Math.round(value)));
  schedulePlotResize();
}

function syncSplitters() {
  setSetupWidth((splitPreferences.setup ?? 0.37) * setupAvailableWidth());
  if (!$(".results-column").offsetHeight) return;
  if (splitPreferences.table !== null) setTableHeight(splitPreferences.table);
  else {
    const divider = $("#results-splitter");
    const {minimum, maximum} = tableLimits();
    divider.setAttribute("aria-valuemin", String(minimum));
    divider.setAttribute("aria-valuemax", String(maximum));
    divider.setAttribute("aria-valuenow", String(Math.round($(".table-panel").getBoundingClientRect().height)));
    schedulePlotResize();
  }
}

function savedSplit(key) {
  try {
    const value = localStorage.getItem(key === "setup" ? "eco-car-setup-ratio" : "eco-car-table-size");
    if (value === null || !Number.isFinite(Number(value))) return null;
    const parsed = Number(value);
    return key === "setup" && (parsed <= 0 || parsed >= 1) ? null : parsed;
  } catch { return null; }
}

function saveSplit(key, value) {
  const stored = key === "setup" && value !== null ? value / setupAvailableWidth() : value;
  splitPreferences[key] = stored;
  try {
    const storageKey = key === "setup" ? "eco-car-setup-ratio" : "eco-car-table-size";
    if (stored === null) localStorage.removeItem(storageKey);
    else localStorage.setItem(storageKey, String(stored));
  } catch { /* Storage may be unavailable in private browsing. */ }
}

function wireSplitter(selector, axis, readSize, applySize, key, reset) {
  const divider = $(selector);
  divider.addEventListener("pointerdown", event => {
    if (event.button !== 0) return;
    event.preventDefault();
    const pointer = event.pointerId;
    const start = axis === "x" ? event.clientX : event.clientY;
    const initial = readSize();
    divider.setPointerCapture(pointer);
    divider.classList.add("dragging");
    document.body.classList.add("resizing");
    document.body.style.cursor = axis === "x" ? "col-resize" : "row-resize";
    const move = next => {
      const coordinate = axis === "x" ? next.clientX : next.clientY;
      applySize(initial + (coordinate - start) * (axis === "x" ? 1 : -1));
    };
    const stop = next => {
      if (next.type === "pointerup") move(next);
      saveSplit(key, readSize());
      divider.classList.remove("dragging");
      document.body.classList.remove("resizing");
      document.body.style.removeProperty("cursor");
      divider.removeEventListener("pointermove", move);
      divider.removeEventListener("pointerup", stop);
      divider.removeEventListener("pointercancel", stop);
      if (divider.hasPointerCapture(pointer)) divider.releasePointerCapture(pointer);
    };
    divider.addEventListener("pointermove", move);
    divider.addEventListener("pointerup", stop);
    divider.addEventListener("pointercancel", stop);
  });
  divider.addEventListener("keydown", event => {
    const direction = axis === "x" ? {ArrowLeft: -1, ArrowRight: 1} : {ArrowUp: 1, ArrowDown: -1};
    if (!(event.key in direction)) return;
    event.preventDefault();
    applySize(readSize() + direction[event.key] * (event.shiftKey ? 40 : 16));
    saveSplit(key, readSize());
  });
  divider.addEventListener("dblclick", reset);
}

function initializeSplitters() {
  splitPreferences.setup = savedSplit("setup");
  splitPreferences.table = savedSplit("table");
  wireSplitter("#workspace-splitter", "x", () => $(".configuration").getBoundingClientRect().width, setSetupWidth, "setup", () => {
    saveSplit("setup", null);
    syncSplitters();
  });
  wireSplitter("#results-splitter", "y", () => $(".table-panel").getBoundingClientRect().height, setTableHeight, "table", () => {
    saveSplit("table", null);
    $(".results-column").classList.remove("table-resized");
    $(".results-column").style.removeProperty("--table-height");
    syncSplitters();
  });
  window.addEventListener("resize", syncSplitters);
  syncSplitters();
}

function invalidateResults() {
  const hadResult = Boolean(state.result);
  state.scenario = null;
  state.result = null;
  $("#result-status").textContent = "AWAITING ANALYSIS";
  $("#export-csv").disabled = true;
  $("#export-xlsx").disabled = true;
  if (hadResult) {
    if (window.Plotly) window.Plotly.purge("chart");
    $("#chart-placeholder").classList.remove("hidden");
    $("#chart-x-label").classList.add("hidden");
    $("#chart-y-label").classList.add("hidden");
    $("#results-body").innerHTML = '<tr><td colspan="9" class="empty-table">Results will appear after analysis.</td></tr>';
  }
}

function format(value, digits = 1) {
  return value === null || value === undefined ? "—" : Number(value).toLocaleString("en-US", {maximumFractionDigits: digits, minimumFractionDigits: digits});
}

function renderTable(rows) {
  let bestIndex = 0;
  rows.forEach((row, index) => {
    if (index > 0 && row.savingsCo2 > (bestIndex === 0 ? 0 : rows[bestIndex].savingsCo2)) bestIndex = index;
  });
  $("#results-body").innerHTML = rows.map((row, index) => `<tr class="${index === bestIndex ? "best-row" : ""}"><td><span class="row-marker" style="--row-color: ${["#84e4b0", "#5c7cfa", "#e8a567", "#a78bfa", "#ee83a8", "#50bacc", "#d5bd69", "#91c476", "#e9a8df"][index]}"></span>${escapeHtml(row.label)}${index === bestIndex ? '<span class="best-badge">Best</span>' : ""}</td><td>${escapeHtml(row.details)}</td><td>${format(row.changeCo2)}</td><td class="${row.savingsCo2 > 0 ? "positive" : ""}">${format(row.savingsCo2)}</td><td>${format(row.yearlyCo2, 2)}</td><td>${format(row.productionPercent)}%</td><td>${format(row.eolPercent)}%</td><td>${format(row.usePercent)}%</td><td>${row.maintenancePercent === null ? "—" : `${format(row.maintenancePercent)}%`}</td></tr>`).join("");
}

function renderTrajectoryChart() {
  const result = state.result;
  const km = state.unit === "km";
  const colors = ["#84e4b0", "#5c7cfa", "#e8a567", "#a78bfa", "#ee83a8", "#50bacc", "#d5bd69", "#91c476", "#e9a8df"];
  const traces = [];
  const current = result.series[0];
  result.series.forEach((car, index) => {
    const xs = km ? car.xKm.map(value => value / 1000) : car.xYears;
    const lastSolid = car.xKm.findLastIndex(value => value <= car.lifeSpanKm);
    const split = Math.max(lastSolid, 0);
    const acquisitionKm = car.xKm[0];
    const currentIndex = current.xKm.findIndex(value => value >= acquisitionKm);
    const baseline = index === 0 ? 0 : current.emissions[Math.max(currentIndex, 0)];
    traces.push({x: [xs[0], xs[0]], y: [baseline, car.emissions[0]], type: "scatter", mode: "lines", showlegend: false, line: {color: colors[index], width: 3}, hoverinfo: "skip"});
    traces.push({x: xs.slice(0, split + 1), y: car.emissions.slice(0, split + 1), type: "scatter", mode: "lines", name: car.label, line: {color: colors[index], width: 3}, hovertemplate: `%{x:,.1f}<br>%{y:,.2f} tCO₂e<extra>${escapeHtml(car.label)}</extra>`});
    if (split < xs.length - 1) traces.push({x: xs.slice(split), y: car.emissions.slice(split), type: "scatter", mode: "lines", showlegend: false, line: {color: colors[index], width: 2, dash: "dash"}, hoverinfo: "skip"});
  });
  const end = km ? result.endKm / 1000 : result.endYears;
  const range = km ? result.kmRange : result.yearsRange;
  const paddedRange = [range[0] - (range[1] - range[0]) * 0.025, range[1]];
  window.Plotly.react("chart", traces, {
    paper_bgcolor: "transparent", plot_bgcolor: "transparent", font: {family: "Inter, Segoe UI, sans-serif", color: "#677a79", size: 12},
    margin: {l: 48, r: 18, t: 16, b: 68}, hovermode: "x unified", dragmode: "pan",
    xaxis: {range: paddedRange, gridcolor: "#e6edeb", zeroline: false},
    yaxis: {range: result.yRange, gridcolor: "#e6edeb", zeroline: false},
    legend: {orientation: "h", y: -0.13, x: 0, font: {size: 10}},
    shapes: [{type: "line", x0: end, x1: end, y0: result.yRange[0], y1: result.yRange[1], line: {color: "#92a2a0", width: 1.5, dash: "dot"}}],
    annotations: [{x: end, y: result.yRange[1], text: "End of usage", showarrow: false, xanchor: "right", yanchor: "top", font: {size: 11, color: "#516663"}}],
  }, {responsive: true, displaylogo: false, scrollZoom: true, modeBarButtonsToRemove: ["toImage"]});
}

function renderBreakdownChart() {
  const rows = state.result.rows;
  const annual = state.barUnit === "annual";
  const phases = [
    ["production", "Production", "#5c7cfa"],
    ["eol", "End of life", "#a78bfa"],
    ["use", "Use", "#e8a567"],
    ["maintenance", "Maintenance / battery", "#4dbb8c"],
  ];
  const traces = phases.map(([key, label, color]) => ({
    type: "bar", name: label, marker: {color}, x: rows.map(row => row.label),
    y: rows.map(row => row.contributions[key][annual ? "annualCo2" : "percent"]),
    customdata: rows.map(row => [row.contributions[key].percent, row.contributions[key].annualCo2]),
    hovertemplate: `${label}<br>%{customdata[0]:.1f}% · %{customdata[1]:.2f} tCO₂e/year<extra>%{x}</extra>`,
  }));
  const maxValue = Math.max(...rows.map(row => annual ? row.yearlyCo2 : 100));
  window.Plotly.react("chart", traces, {
    paper_bgcolor: "transparent", plot_bgcolor: "transparent", font: {family: "Inter, Segoe UI, sans-serif", color: "#677a79", size: 11},
    margin: {l: 48, r: 18, t: 18, b: 72}, barmode: "relative", bargap: 0.38,
    xaxis: {type: "category", gridcolor: "#e6edeb", zeroline: false, tickfont: {size: 10}},
    yaxis: {rangemode: "tozero", range: [0, maxValue * 1.08], gridcolor: "#e6edeb", zeroline: false, ticksuffix: annual ? "" : "%"},
    legend: {orientation: "h", y: -0.18, x: 0, font: {size: 10}},
    hovermode: "closest", dragmode: "pan",
  }, {responsive: true, displaylogo: false, modeBarButtonsToRemove: ["toImage"]});
}

function renderChart() {
  if (!state.result || !window.Plotly) return;
  const breakdown = state.chartType === "breakdown";
  $("#chart-x-label").textContent = breakdown ? "Vehicle" : state.unit === "km" ? "Current car mileage (1,000 km)" : "Current car age (years)";
  $("#chart-y-label").textContent = breakdown ? state.barUnit === "annual" ? "Annual CO₂e (tCO₂e/year)" : "Share of annual CO₂e (%)" : "Cumulative CO₂e (tCO₂e)";
  $("#chart-x-label").classList.remove("hidden");
  $("#chart-y-label").classList.remove("hidden");
  $("#chart").setAttribute("aria-label", breakdown ? `Annual emissions by life-cycle phase, ${state.barUnit === "annual" ? "tonnes of CO2 equivalent per year" : "percentage"}` : "Life-cycle emissions trajectory");
  if (breakdown) renderBreakdownChart();
  else renderTrajectoryChart();
}

function renderResults(result) {
  $("#chart-placeholder").classList.add("hidden");
  $("#result-status").textContent = "ANALYSIS READY";
  $("#export-csv").disabled = false;
  $("#export-xlsx").disabled = false;
  renderTable(result.rows);
  renderChart();
  requestAnimationFrame(syncSplitters);
}

async function compute() {
  showError("");
  if (state.pendingDefaults > 0) { showError("Please wait while vehicle defaults load."); return; }
  const required = $$("input:required").find(input => !input.closest(".field.hidden, .secondhand-fields.hidden, #end-usage-fields.hidden") && !input.checkValidity());
  if (required) {
    selectView("setup");
    selectConfigTab(required.closest("[data-config-panel]").dataset.configPanel);
    required.closest("details")?.setAttribute("open", "");
    required.reportValidity(); required.focus(); return;
  }
  const button = $("#compute");
  button.disabled = true;
  button.firstElementChild.textContent = "Calculating…";
  try {
    const scenario = scenarioFromForms();
    if (!scenario.settings.keepEOL && !$("#keep-lifespan").value) throw new Error("Enter the intended end of usage.");
    const response = await request("/api/analyze", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(scenario)});
    state.result = await response.json();
    state.scenario = scenario;
    if (matchMedia("(max-width: 700px)").matches) selectView("results");
    renderResults(state.result);
  } catch (error) { invalidateResults(); showError(error.message); }
  finally { button.disabled = false; button.firstElementChild.textContent = "Run analysis"; }
}

async function exportResult(formatName) {
  if (!state.scenario) return;
  try {
    const response = await request(`/api/export/${formatName}`, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(state.scenario)});
    const url = URL.createObjectURL(await response.blob());
    const link = document.createElement("a");
    link.href = url;
    link.download = `car_data_export.${formatName}`;
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  } catch (error) { showError(error.message); }
}

async function initialize() {
  try {
    initializeSplitters();
    $$("[data-config-tab]").forEach(button => button.addEventListener("click", () => selectConfigTab(button.dataset.configTab)));
    $$("[data-view]").forEach(button => button.addEventListener("click", () => selectView(button.dataset.view)));
    state.config = await (await request("/api/config")).json();
    state.current = structuredClone(state.config.defaults.current);
    state.alternatives = [structuredClone(state.config.defaults.replacement)];
    $("#annual-mileage").value = state.config.defaults.settings.km2yearsConvFactor;
    $("#ice-lifespan").value = state.config.defaults.settings.ICElifeSpan;
    $("#bev-lifespan").value = state.config.defaults.settings.BEVlifeSpan;
    renderVehicles();
    $("#add-car").addEventListener("click", () => {
      if (state.alternatives.length >= 8) { showError("A maximum of eight replacement cars can be compared."); return; }
      storeVehicleForms(); state.alternatives.push(structuredClone(state.config.defaults.replacement)); renderVehicles(); invalidateResults();
    });
    document.addEventListener("change", async event => {
      if (event.target.matches("input, select")) invalidateResults();
      const form = event.target.closest(".vehicle-form");
      if (form) {
        const key = event.target.dataset.field;
        if (key === "carSegment" || key === "engineType") await updateDefaults(form);
        if (key === "country") $('[data-field="energyMix"]', form).value = state.config.energyMix[event.target.value] ?? "";
        if (key === "secondHandCar" || key === "engineType" || key === "country") setVehicleVisibility(form);
      }
      if (event.target.id === "keep-eol") $("#end-usage-fields").classList.toggle("hidden", event.target.checked);
      if (event.target.id === "bev-lifespan") $$('.vehicle-form').forEach(vehicleForm => {
        if ($('[data-field="engineType"]', vehicleForm).value === "BEV") $('[data-field="batteryLifeTime"]', vehicleForm).value = event.target.value;
      });
    });
    document.addEventListener("input", event => { if (event.target.matches("input")) invalidateResults(); });
    document.addEventListener("click", async event => {
      const reset = event.target.closest(".reset-vehicle");
      if (reset) await updateDefaults(reset.closest(".vehicle-form"), true);
    });
    $("#compute").addEventListener("click", compute);
    $("#export-csv").addEventListener("click", () => exportResult("csv"));
    $("#export-xlsx").addEventListener("click", () => exportResult("xlsx"));
    $$("[data-chart-type]").forEach(button => button.addEventListener("click", () => {
      state.chartType = button.dataset.chartType;
      $$("[data-chart-type]").forEach(item => { item.classList.toggle("selected", item === button); item.setAttribute("aria-pressed", item === button ? "true" : "false"); });
      $("#trajectory-units").classList.toggle("hidden", state.chartType !== "trajectory");
      $("#breakdown-units").classList.toggle("hidden", state.chartType !== "breakdown");
      renderChart();
    }));
    $$("[data-unit]").forEach(button => button.addEventListener("click", () => {
      state.unit = button.dataset.unit;
      $$("[data-unit]").forEach(item => { item.classList.toggle("selected", item === button); item.setAttribute("aria-pressed", item === button ? "true" : "false"); });
      renderChart();
    }));
    $$("[data-bar-unit]").forEach(button => button.addEventListener("click", () => {
      state.barUnit = button.dataset.barUnit;
      $$("[data-bar-unit]").forEach(item => { item.classList.toggle("selected", item === button); item.setAttribute("aria-pressed", item === button ? "true" : "false"); });
      renderChart();
    }));
  } catch (error) { showError(`Unable to initialize the application: ${error.message}`); }
}

initialize();

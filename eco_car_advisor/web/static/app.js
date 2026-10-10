"use strict";

const state = { config: null, alternatives: [], result: null, scenario: null, unit: "years", pendingDefaults: 0 };
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
    $("#results-body").innerHTML = '<tr><td colspan="9" class="empty-table">Results will appear after analysis.</td></tr>';
    $("#best-saving").innerHTML = '— <small>tCO₂e</small>';
    $("#insight-copy").textContent = "Run your analysis to compare the updated vehicle inputs.";
  }
}

function format(value, digits = 1) {
  return value === null || value === undefined ? "—" : Number(value).toLocaleString("en-US", {maximumFractionDigits: digits, minimumFractionDigits: digits});
}

function renderTable(rows) {
  $("#results-body").innerHTML = rows.map((row, index) => `<tr><td><span class="row-marker" style="--row-color: ${["#84e4b0", "#5c7cfa", "#e8a567", "#a78bfa", "#ee83a8", "#50bacc", "#d5bd69", "#91c476", "#e9a8df"][index]}"></span>${escapeHtml(row.label)}</td><td>${escapeHtml(row.details)}</td><td>${format(row.changeCo2)}</td><td class="${row.savingsCo2 > 0 ? "positive" : ""}">${format(row.savingsCo2)}</td><td>${format(row.yearlyCo2, 2)}</td><td>${format(row.productionPercent)}%</td><td>${format(row.eolPercent)}%</td><td>${format(row.usePercent)}%</td><td>${row.maintenancePercent === null ? "—" : `${format(row.maintenancePercent)}%`}</td></tr>`).join("");
}

function renderChart() {
  if (!state.result || !window.Plotly) return;
  const result = state.result;
  const km = state.unit === "km";
  const colors = ["#84e4b0", "#5c7cfa", "#e8a567", "#a78bfa", "#ee83a8", "#50bacc", "#d5bd69", "#91c476", "#e9a8df"];
  const traces = [];
  const shapes = [];
  result.series.forEach((car, index) => {
    const xs = km ? car.xKm.map(value => value / 1000) : car.xYears;
    const lastSolid = car.xKm.findLastIndex(value => value <= car.lifeSpanKm);
    const split = Math.max(lastSolid, 0);
    traces.push({x: xs.slice(0, split + 1), y: car.emissions.slice(0, split + 1), type: "scatter", mode: "lines", name: car.label, line: {color: colors[index], width: 3}, hovertemplate: `%{x:,.1f}<br>%{y:,.2f} tCO₂e<extra>${escapeHtml(car.label)}</extra>`});
    if (split < xs.length - 1) traces.push({x: xs.slice(split), y: car.emissions.slice(split), type: "scatter", mode: "lines", showlegend: false, line: {color: colors[index], width: 2, dash: "dash"}, hoverinfo: "skip"});
    shapes.push({type: "line", x0: xs[0], x1: xs[0], y0: index === 0 ? 0 : result.emissionsAtReplacement, y1: car.emissions[0], line: {color: colors[index], width: 2}});
  });
  const end = km ? result.endKm / 1000 : result.endYears;
  const range = km ? result.kmRange : result.yearsRange;
  window.Plotly.react("chart", traces, {
    paper_bgcolor: "transparent", plot_bgcolor: "transparent", font: {family: "Inter, Segoe UI, sans-serif", color: "#677a79", size: 12},
    margin: {l: 62, r: 18, t: 25, b: 54}, hovermode: "x unified", dragmode: "pan",
    xaxis: {title: km ? "Current car mileage (1,000 km)" : "Current car age (years)", range, gridcolor: "#e6edeb", zeroline: false},
    yaxis: {title: "tCO₂e", range: result.yRange, gridcolor: "#e6edeb", zeroline: false},
    legend: {orientation: "h", y: -0.25, x: 0, font: {size: 11}},
    shapes: [...shapes, {type: "line", x0: end, x1: end, y0: result.yRange[0], y1: result.yRange[1], line: {color: "#92a2a0", width: 1.5, dash: "dot"}}],
    annotations: [{x: end, y: result.yRange[1], text: "End of usage", showarrow: false, xanchor: "right", yanchor: "top", font: {size: 11, color: "#516663"}}],
  }, {responsive: true, displaylogo: false, scrollZoom: true, modeBarButtonsToRemove: ["toImage"]});
}

function renderResults(result) {
  $("#chart-placeholder").classList.add("hidden");
  $("#result-status").textContent = "ANALYSIS READY";
  $("#export-csv").disabled = false;
  $("#export-xlsx").disabled = false;
  renderTable(result.rows);
  const ranked = result.rows.slice(1).sort((a, b) => b.savingsCo2 - a.savingsCo2);
  const best = ranked[0];
  $("#best-saving").innerHTML = `${format(best.savingsCo2)} <small>tCO₂e</small>`;
  $("#insight-copy").textContent = `${best.label} · ${best.details} compared with keeping your current car through ${format(result.endKm, 0)} km.`;
  renderChart();
}

async function compute() {
  showError("");
  if (state.pendingDefaults > 0) { showError("Please wait while vehicle defaults load."); return; }
  const required = $$("input:required").find(input => !input.closest(".hidden") && !input.checkValidity());
  if (required) { required.closest("details")?.setAttribute("open", ""); required.reportValidity(); required.focus(); return; }
  const button = $("#compute");
  button.disabled = true;
  button.firstElementChild.textContent = "Calculating…";
  try {
    const scenario = scenarioFromForms();
    if (!scenario.settings.keepEOL && !$("#keep-lifespan").value) throw new Error("Enter the intended end of usage.");
    const response = await request("/api/analyze", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(scenario)});
    state.result = await response.json();
    state.scenario = scenario;
    renderResults(state.result);
  } catch (error) { invalidateResults(); showError(error.message); }
  finally { button.disabled = false; button.firstElementChild.textContent = "Run carbon analysis"; }
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
    $$("[data-unit]").forEach(button => button.addEventListener("click", () => {
      state.unit = button.dataset.unit;
      $$("[data-unit]").forEach(item => { item.classList.toggle("selected", item === button); item.setAttribute("aria-pressed", item === button ? "true" : "false"); });
      renderChart();
    }));
  } catch (error) { showError(`Unable to initialize the application: ${error.message}`); }
}

initialize();

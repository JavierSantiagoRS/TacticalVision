"use strict";

/* ============================================================
   TACTICALVISION DASHBOARD
   app.js
   ============================================================ */

const API = "http://127.0.0.1:8000";

let eventChart = null;
let refreshTimer = null;

/* ============================================================
   HELPERS
   ============================================================ */

function $(id) {
  return document.getElementById(id);
}

function escapeHTML(value) {
  if (value === null || value === undefined) {
    return "";
  }

  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatConfidence(value) {
  if (value === null || value === undefined || value === "") {
    return "--";
  }

  const number = Number(value);

  if (Number.isNaN(number)) {
    return escapeHTML(value);
  }

  return `${(number * 100).toFixed(1)}%`;
}

function formatDate(value) {
  if (!value) {
    return "--";
  }

  try {
    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return escapeHTML(value);
    }

    return date.toLocaleString();
  } catch {
    return escapeHTML(value);
  }
}

function normalize(value) {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, " ");
}

/* ============================================================
   API
   ============================================================ */

async function apiFetch(endpoint) {
  const response = await fetch(`${API}${endpoint}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status} - ${endpoint}`);
  }

  return await response.json();
}

/* ============================================================
   STATUS
   ============================================================ */

async function loadStatus() {
  const systemStatus = $("system-status");
  const eventsElement = $("events");
  const systemEvents = $("system-events");
  const apiStatus = $("api-status");
  const sidebarStatus = $("sidebar-status");
  const liveDot = $("live-dot");
  const sidebarDot = $("sidebar-dot");

  try {
    const data = await apiFetch("/api/status");

    const online = data.status === "online";

    if (systemStatus) {
      systemStatus.textContent = online ? "SYSTEM ONLINE" : "SYSTEM OFFLINE";
    }

    if (apiStatus) {
      apiStatus.textContent = online ? "ONLINE" : "OFFLINE";
    }

    if (sidebarStatus) {
      sidebarStatus.textContent = online ? "ONLINE" : "OFFLINE";
    }

    if (liveDot) {
      liveDot.classList.toggle("offline", !online);
    }

    if (sidebarDot) {
      sidebarDot.classList.toggle("offline", !online);
    }

    if (eventsElement) {
      eventsElement.textContent = data.events ?? "--";
    }

    if (systemEvents) {
      systemEvents.textContent = data.events ?? "--";
    }
  } catch (error) {
    console.error("[STATUS]", error);

    if (systemStatus) {
      systemStatus.textContent = "SYSTEM OFFLINE";
    }

    if (apiStatus) {
      apiStatus.textContent = "OFFLINE";
    }

    if (sidebarStatus) {
      sidebarStatus.textContent = "OFFLINE";
    }

    if (liveDot) {
      liveDot.classList.add("offline");
    }

    if (sidebarDot) {
      sidebarDot.classList.add("offline");
    }
  }
}

/* ============================================================
   TOTAL EVENTS
   ============================================================ */

async function loadEventCount() {
  try {
    const data = await apiFetch("/api/events/count");

    const total = data.total ?? 0;

    const element = $("total-events");

    if (element) {
      element.textContent = total;
    }

    const overviewEvents = $("events");

    if (overviewEvents) {
      overviewEvents.textContent = total;
    }
  } catch (error) {
    console.error("[EVENT COUNT]", error);
  }
}

/* ============================================================
   EVENT TYPES
   ============================================================ */

async function loadEventTypes() {
  try {
    const rows = await apiFetch("/api/events/types");

    let alerts = 0;
    let anomalies = 0;

    rows.forEach((row) => {
      const type = normalize(row.event_type ?? row.type ?? row.name);

      const count = Number(row.count ?? row.total ?? 0);

      if (type === "alert") {
        alerts += count;
      }

      if (type === "anomaly") {
        anomalies += count;
      }
    });

    const alertsElement = $("alerts");

    const anomaliesElement = $("anomalies");

    if (alertsElement) {
      alertsElement.textContent = alerts;
    }

    if (anomaliesElement) {
      anomaliesElement.textContent = anomalies;
    }

    renderEventChart(rows);
  } catch (error) {
    console.error("[EVENT TYPES]", error);
  }
}

/* ============================================================
   EVENT CHART
   ============================================================ */

function renderEventChart(rows) {
  const canvas = $("event-chart");

  if (!canvas) {
    return;
  }

  if (typeof Chart === "undefined") {
    console.warn("Chart.js no está cargado.");
    return;
  }

  const labels = [];
  const values = [];

  rows.forEach((row) => {
    const label = row.event_type ?? row.type ?? row.name ?? "UNKNOWN";

    const value = Number(row.count ?? row.total ?? 0);

    labels.push(label);
    values.push(value);
  });

  if (eventChart) {
    eventChart.destroy();
  }

  eventChart = new Chart(canvas.getContext("2d"), {
    type: "doughnut",

    data: {
      labels,
      datasets: [
        {
          data: values,
        },
      ],
    },

    options: {
      responsive: true,
      maintainAspectRatio: false,

      plugins: {
        legend: {
          position: "bottom",
        },
      },
    },
  });
}

/* ============================================================
   OBJECT CLASSES
   ============================================================ */

async function loadClasses() {
  try {
    const rows = await apiFetch("/api/events/classes");

    renderClasses(rows);

    updateObjectClassCount(rows);
  } catch (error) {
    console.error("[CLASSES]", error);
  }
}

function renderClasses(rows) {
  const container = $("object-classes");

  if (!container) {
    return;
  }

  container.innerHTML = "";

  rows.forEach((row) => {
    const className =
      row.object_class ?? row.class_name ?? row.class ?? row.name ?? "unknown";

    const count = Number(row.count ?? row.total ?? 0);

    const item = document.createElement("div");

    item.className = "class-row";

    item.innerHTML = `
            <div class="class-info">
                <span>${escapeHTML(className)}</span>
                <strong>${count}</strong>
            </div>

            <div class="class-bar">
                <div
                    class="class-bar-fill"
                    style="width:${Math.min(count, 100)}%"
                ></div>
            </div>
        `;

    container.appendChild(item);
  });
}

function updateObjectClassCount(rows) {
  const elements = [$("classes"), $("object-classes-count")];

  elements.forEach((element) => {
    if (element) {
      element.textContent = rows.length;
    }
  });
}

/* ============================================================
   ZONES
   ============================================================ */

async function loadZones() {
  try {
    const rows = await apiFetch("/api/events/zones");

    renderZones(rows);
  } catch (error) {
    console.error("[ZONES]", error);
  }
}

function renderZones(rows) {
  const container = $("zone-activity");

  if (!container) {
    return;
  }

  container.innerHTML = "";

  rows.forEach((row) => {
    const zone = row.zone_name ?? row.zone ?? "NO_ZONE";

    const count = Number(row.count ?? row.total ?? 0);

    const item = document.createElement("div");

    item.className = "zone-row";

    item.innerHTML = `
            <div class="zone-info">
                <span>${escapeHTML(zone)}</span>
                <strong>${count}</strong>
            </div>

            <div class="zone-bar">
                <div
                    class="zone-bar-fill"
                    style="width:${Math.min(count, 100)}%"
                ></div>
            </div>
        `;

    container.appendChild(item);
  });
}

/* ============================================================
   RECENT EVENTS
   ============================================================ */

async function loadEvents() {
  try {
    const events = await apiFetch("/api/events?limit=20");

    renderRecentEvents(events);
  } catch (error) {
    console.error("[RECENT EVENTS]", error);
  }
}

function renderRecentEvents(events) {
  const tbody = $("recent-events-body");

  if (!tbody) {
    return;
  }

  tbody.innerHTML = "";

  events.forEach((event) => {
    const row = document.createElement("tr");

    const id = event.id ?? "--";

    const objectId = event.object_id ?? "--";

    const className = event.object_class ?? event.class_name ?? event.class ?? "--";

    const type = event.event_type ?? event.type ?? "--";

    const zone = event.zone_name ?? event.zone ?? "NO_ZONE";

    const confidence = formatConfidence(event.confidence);

    const timestamp = event.timestamp ?? event.created_at ?? "--";

    row.innerHTML = `
            <td>${escapeHTML(id)}</td>

            <td>${escapeHTML(timestamp)}</td>

            <td>#${escapeHTML(objectId)}</td>

            <td>${escapeHTML(className)}</td>

            <td>${escapeHTML(type)}</td>

            <td>${escapeHTML(zone)}</td>

            <td>${confidence}</td>
        `;

    tbody.appendChild(row);
  });
}

/* ============================================================
   OVERVIEW
   ============================================================ */

async function refreshOverview() {
  await Promise.allSettled([
    loadStatus(),
    loadEventCount(),
    loadEventTypes(),
    loadClasses(),
    loadZones(),
    loadEvents(),
  ]);
}

/* ============================================================
   EVENTS VIEW
   ============================================================ */

let allEvents = [];

async function loadEventsView() {
  try {
    allEvents = await apiFetch("/api/events?limit=100");

    populateEventFilters(allEvents);

    renderEventsView(allEvents);
  } catch (error) {
    console.error("[EVENTS VIEW]", error);

    const tbody = $("events-table-body");

    if (tbody) {
      tbody.innerHTML = `
                <tr>
                    <td colspan="7">
                        Unable to load events.
                    </td>
                </tr>
            `;
    }
  }
}

function populateEventFilters(events) {
  populateSelect(
    "filter-type",
    events.map((event) => event.event_type ?? event.type),
  );

  populateSelect(
    "filter-class",
    events.map((event) => event.object_class ?? event.class_name ?? event.class),
  );

  populateSelect(
    "filter-zone",
    events.map((event) => event.zone_name ?? event.zone),
  );
}

function populateSelect(id, values) {
  const select = $(id);

  if (!select) {
    return;
  }

  const current = select.value;

  const unique = [...new Set(values.filter(Boolean).map(String))].sort();

  const firstOption = select.options[0]?.textContent ?? "All";

  select.innerHTML = "";

  const allOption = document.createElement("option");

  allOption.value = "";
  allOption.textContent = firstOption;

  select.appendChild(allOption);

  unique.forEach((value) => {
    const option = document.createElement("option");

    option.value = value;
    option.textContent = value;

    select.appendChild(option);
  });

  if (unique.includes(current)) {
    select.value = current;
  }
}

function renderEventsView(events) {
  const tbody = $("events-table-body");

  const counter = $("events-count");

  if (!tbody) {
    return;
  }

  tbody.innerHTML = "";

  if (counter) {
    counter.textContent = `${events.length} EVENTS`;
  }

  if (!events.length) {
    tbody.innerHTML = `
            <tr>
                <td colspan="7">
                    NO EVENTS FOUND
                </td>
            </tr>
        `;

    return;
  }

  events.forEach((event) => {
    const row = document.createElement("tr");

    row.innerHTML = `
            <td>
                ${escapeHTML(event.id ?? "--")}
            </td>

            <td>
                ${escapeHTML(event.timestamp ?? event.created_at ?? "--")}
            </td>

            <td>
                #${escapeHTML(event.object_id ?? "--")}
            </td>

            <td>
                ${escapeHTML(event.object_class ?? event.class_name ?? event.class ?? "--")}
            </td>

            <td>
                ${escapeHTML(event.event_type ?? event.type ?? "--")}
            </td>

            <td>
                ${escapeHTML(event.zone_name ?? event.zone ?? "NO_ZONE")}
            </td>

            <td>
                ${formatConfidence(event.confidence)}
            </td>
        `;

    tbody.appendChild(row);
  });
}

/* ============================================================
   EVENT FILTERS
   ============================================================ */

function filterEvents() {
  const type = normalize($("filter-type")?.value);

  const className = normalize($("filter-class")?.value);

  const zone = normalize($("filter-zone")?.value);

  const search = normalize($("filter-search")?.value);

  const filtered = allEvents.filter((event) => {
    const eventType = normalize(event.event_type ?? event.type);

    const eventClass = normalize(event.object_class ?? event.class_name ?? event.class);

    const eventZone = normalize(event.zone_name ?? event.zone);

    const objectId = normalize(event.object_id);

    if (type && eventType !== type) {
      return false;
    }

    if (className && eventClass !== className) {
      return false;
    }

    if (zone && eventZone !== zone) {
      return false;
    }

    if (search && !objectId.includes(search)) {
      return false;
    }

    return true;
  });

  renderEventsView(filtered);
}

/* ============================================================
   OBJECTS VIEW
   ============================================================ */

async function loadObjectsView() {
  const container = $("objects-container");

  if (!container) {
    return;
  }

  try {
    const events = await apiFetch("/api/events?limit=100");

    const objects = {};

    events.forEach((event) => {
      const id = event.object_id;

      if (id === null || id === undefined) {
        return;
      }

      if (!objects[id]) {
        objects[id] = {
          id,
          className: event.object_class ?? event.class_name ?? event.class ?? "--",

          zone: event.zone_name ?? event.zone ?? "NO_ZONE",

          confidence: event.confidence,

          events: 0,

          lastEvent: event.timestamp ?? event.created_at ?? "--",
        };
      }

      objects[id].events++;

      objects[id].lastEvent =
        event.timestamp ?? event.created_at ?? objects[id].lastEvent;
    });

    renderObjectsView(Object.values(objects));
  } catch (error) {
    console.error("[OBJECTS]", error);

    container.innerHTML = `
            <div class="card">
                <h2>Objects</h2>
                <p>Unable to load tracked objects.</p>
            </div>
        `;
  }
}

function renderObjectsView(objects) {
  const container = $("objects-container");

  if (!container) {
    return;
  }

  if (!objects.length) {
    container.innerHTML = `
            <div class="card">
                <h2>Tracked Objects</h2>
                <p>No tracked objects available.</p>
            </div>
        `;

    return;
  }

  container.innerHTML = `
        <div class="card">

            <div class="card-header">
                <h2>Tracked Objects</h2>
                <span>
                    ${objects.length} OBJECTS
                </span>
            </div>

            <div class="table-wrapper">

                <table class="events-table">

                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>CLASS</th>
                            <th>ZONE</th>
                            <th>CONFIDENCE</th>
                            <th>EVENTS</th>
                            <th>LAST EVENT</th>
                        </tr>
                    </thead>

                    <tbody>

                        ${objects
                          .map(
                            (object) => `

                            <tr>

                                <td>
                                    #${escapeHTML(object.id)}
                                </td>

                                <td>
                                    ${escapeHTML(object.className)}
                                </td>

                                <td>
                                    ${escapeHTML(object.zone)}
                                </td>

                                <td>
                                    ${formatConfidence(object.confidence)}
                                </td>

                                <td>
                                    ${object.events}
                                </td>

                                <td>
                                    ${escapeHTML(object.lastEvent)}
                                </td>

                            </tr>

                        `,
                          )
                          .join("")}

                    </tbody>

                </table>

            </div>

        </div>
    `;
}

/* ============================================================
   ZONES VIEW
   ============================================================ */

async function loadZonesView() {
  const container = $("zones-container");

  if (!container) {
    return;
  }

  try {
    const rows = await apiFetch("/api/events/zones");

    if (!rows.length) {
      container.innerHTML = `
                <div class="card">
                    <h2>Zones</h2>
                    <p>No zone activity available.</p>
                </div>
            `;

      return;
    }

    container.innerHTML = `
            <div class="card">

                <div class="card-header">
                    <h2>Zone Activity</h2>
                    <span>
                        ${rows.length} ZONES
                    </span>
                </div>

                <div class="zone-grid">

                    ${rows
                      .map((row) => {
                        const zone = row.zone_name ?? row.zone ?? "NO_ZONE";

                        const count = Number(row.count ?? row.total ?? 0);

                        return `

                            <div class="zone-card">

                                <div>
                                    <span class="muted">
                                        ZONE
                                    </span>

                                    <h3>
                                        ${escapeHTML(zone)}
                                    </h3>
                                </div>

                                <strong>
                                    ${count}
                                </strong>

                            </div>

                        `;
                      })
                      .join("")}

                </div>

            </div>
        `;
  } catch (error) {
    console.error("[ZONES VIEW]", error);

    container.innerHTML = `
            <div class="card">
                <h2>Zones</h2>
                <p>Unable to load zone activity.</p>
            </div>
        `;
  }
}

/* ============================================================
   ANALYTICS VIEW
   ============================================================ */

async function loadAnalyticsView() {
  const container = $("analytics-container");

  if (!container) {
    return;
  }

  try {
    const [types, classes, zones] = await Promise.all([
      apiFetch("/api/events/types"),

      apiFetch("/api/events/classes"),

      apiFetch("/api/events/zones"),
    ]);

    const totalTypes = types.reduce(
      (sum, row) => sum + Number(row.count ?? row.total ?? 0),
      0,
    );

    const totalClasses = classes.reduce(
      (sum, row) => sum + Number(row.count ?? row.total ?? 0),
      0,
    );

    const totalZones = zones.reduce(
      (sum, row) => sum + Number(row.count ?? row.total ?? 0),
      0,
    );

    container.innerHTML = `

            <div class="kpi-grid">

                <div class="kpi-card">
                    <span>EVENT TYPES</span>
                    <strong>${types.length}</strong>
                </div>

                <div class="kpi-card">
                    <span>OBJECT CLASSES</span>
                    <strong>${classes.length}</strong>
                </div>

                <div class="kpi-card">
                    <span>ZONE EVENTS</span>
                    <strong>${totalZones}</strong>
                </div>

                <div class="kpi-card">
                    <span>CLASS EVENTS</span>
                    <strong>${totalClasses}</strong>
                </div>

            </div>


            <div class="card">

                <div class="card-header">
                    <h2>Event Distribution</h2>
                    <span>
                        ${totalTypes} EVENTS
                    </span>
                </div>

                <div class="analytics-list">

                    ${types
                      .map(
                        (row) => `

                        <div class="analytics-row">

                            <span>
                                ${escapeHTML(
                                  row.event_type ??
                                    row.type ??
                                    row.name ??
                                    "UNKNOWN",
                                )}
                            </span>

                            <strong>
                                ${Number(row.count ?? row.total ?? 0)}
                            </strong>

                        </div>

                    `,
                      )
                      .join("")}

                </div>

            </div>

        `;
  } catch (error) {
    console.error("[ANALYTICS]", error);

    container.innerHTML = `
            <div class="card">
                <h2>Analytics</h2>
                <p>Unable to load analytics.</p>
            </div>
        `;
  }
}

/* ============================================================
   SYSTEM VIEW
   ============================================================ */

async function loadSystemView() {
  const container = $("system-container");

  if (!container) {
    return;
  }

  try {
    const status = await apiFetch("/api/status");

    const online = status.status === "online";

    container.innerHTML = `

            <div class="card">

                <div class="card-header">
                    <h2>System Status</h2>

                    <span class="${
                      online ? "status-online" : "status-offline"
                    }">

                        ${online ? "ONLINE" : "OFFLINE"}

                    </span>

                </div>


                <div class="system-grid">

                    <div class="system-item">

                        <span>API</span>

                        <strong>
                            ${online ? "ONLINE" : "OFFLINE"}
                        </strong>

                    </div>


                    <div class="system-item">

                        <span>DATABASE</span>

                        <strong>
                            ONLINE
                        </strong>

                    </div>


                    <div class="system-item">

                        <span>EVENTS</span>

                        <strong>
                            ${status.events ?? 0}
                        </strong>

                    </div>


                    <div class="system-item">

                        <span>RUNTIME</span>

                        <strong>
                            ACTIVE
                        </strong>

                    </div>

                </div>

            </div>

        `;
  } catch (error) {
    console.error("[SYSTEM]", error);

    container.innerHTML = `
            <div class="card">
                <h2>System Status</h2>
                <p>API OFFLINE</p>
            </div>
        `;
  }
}

/* ============================================================
   NAVIGATION
   ============================================================ */

const ROUTES = Object.freeze([
  "overview",
  "events",
  "objects",
  "zones",
  "analytics",
  "system",
]);

/* ============================================================
   GET CURRENT ROUTE
   ============================================================ */

function getCurrentRoute() {
  const hash = window.location.hash.replace(/^#/, "").trim().toLowerCase();

  if (ROUTES.includes(hash)) {
    return hash;
  }

  return "overview";
}

/* ============================================================
   SET ACTIVE NAVIGATION ITEM
   ============================================================ */

function updateNavigation(route) {
  document.querySelectorAll(".sidebar-nav .nav-item").forEach((item) => {
    const itemRoute = normalize(
      item.dataset.route ??
        item.dataset.view ??
        item.getAttribute("href")?.replace(/^#/, ""),
    );

    const active = itemRoute === route;

    item.classList.toggle("active", active);

    if (active) {
      item.setAttribute("aria-current", "page");
    } else {
      item.removeAttribute("aria-current");
    }
  });
}

/* ============================================================
   SHOW VIEW
   ============================================================ */

async function showView(route) {
  if (!ROUTES.includes(route)) {
    route = "overview";
  }

  /*
   * Ocultar todas las vistas
   */

  document.querySelectorAll(".view").forEach((view) => {
    view.classList.remove("active");
  });

  /*
   * Mostrar únicamente la vista seleccionada
   */

  const target = document.getElementById(`view-${route}`);

  if (!target) {
    console.error(`[NAVIGATION] View not found: view-${route}`);

    return;
  }

  target.classList.add("active");

  /*
   * Sidebar
   */

  updateNavigation(route);

  /*
   * Título
   */

  const titles = {
    overview: "Overview",
    events: "Events",
    objects: "Objects",
    zones: "Zones",
    analytics: "Analytics",
    system: "System",
  };

  document.title = `TacticalVision — ${titles[route]}`;

  /*
   * Cargar datos de la sección
   */

  switch (route) {
    case "overview":
      await refreshOverview();

      break;

    case "events":
      await loadEventsView();

      break;

    case "objects":
      await loadObjectsView();

      break;

    case "zones":
      await loadZonesView();

      break;

    case "analytics":
      await loadAnalyticsView();

      break;

    case "system":
      await loadSystemView();

      break;
  }
}

/* ============================================================
   NAVIGATE
   ============================================================ */

function navigate(route) {
  if (!ROUTES.includes(route)) {
    route = "overview";
  }

  const targetHash = `#${route}`;

  /*
   * Si ya estamos en la ruta,
   * simplemente renderizarla.
   */

  if (window.location.hash === targetHash) {
    showView(route);

    return;
  }

  /*
   * Cambiar URL.
   *
   * Esto dispara automáticamente
   * hashchange.
   */

  window.location.hash = route;
}

/* ============================================================
   SIDEBAR CLICK HANDLER
   ============================================================ */

document.addEventListener(
  "click",
  (event) => {
    const item = event.target.closest(".sidebar-nav .nav-item");

    if (!item) {
      return;
    }

    let route = item.dataset.route ?? item.dataset.view;

    if (!route) {
      route = item.getAttribute("href")?.replace(/^#/, "");
    }

    route = normalize(route);

    if (!ROUTES.includes(route)) {
      console.warn("[NAVIGATION] Invalid route:", route);

      return;
    }

    event.preventDefault();

    navigate(route);
  },
  true,
);

/* ============================================================
   HASH CHANGE
   ============================================================ */

window.addEventListener("hashchange", () => {
  const route = getCurrentRoute();

  showView(route);
});

/* ============================================================
   EXTERNAL ROUTING API
   ============================================================ */

window.TacticalVisionNavigation = {
  navigate,

  showView,

  getCurrentRoute,
};

/* ============================================================
   CLOCK
   ============================================================ */

function updateClock() {
  const elements = [$("clock"), $("current-time"), $("time")];

  const now = new Date();

  const time = now.toLocaleTimeString();

  elements.forEach((element) => {
    if (element) {
      element.textContent = time;
    }
  });
}

/* ============================================================
   REFRESH DASHBOARD
   ============================================================ */

async function refreshDashboard() {
  const route = getCurrentRoute();

  switch (route) {
    case "overview":
      await refreshOverview();
      break;

    case "events":
      await loadEventsView();
      break;

    case "objects":
      await loadObjectsView();
      break;

    case "zones":
      await loadZonesView();
      break;

    case "analytics":
      await loadAnalyticsView();
      break;

    case "system":
      await loadSystemView();
      break;

    default:
      await refreshOverview();
      break;
  }
}

/* ============================================================
   INITIALIZATION
   ============================================================ */

async function initializeDashboard() {
  console.log("[TacticalVision] Dashboard initializing...");

  /*
   * Si no existe hash, comenzar en Overview.
   */
  if (!window.location.hash) {
    history.replaceState(null, "", "#overview");
  }

  /*
   * Mostrar la sección actual.
   */
  await showView(getCurrentRoute());

  /*
   * Reloj
   */
  updateClock();
  setInterval(updateClock, 1000);

  /*
   * Primera actualización.
   */
  await refreshDashboard();

  $("refresh-btn")?.addEventListener("click", refreshDashboard);
  $("events-refresh")?.addEventListener("click", loadEventsView);
  ["filter-type", "filter-class", "filter-zone"].forEach((id) => {
    $(id)?.addEventListener("change", filterEvents);
  });
  $("filter-search")?.addEventListener("input", filterEvents);

  /*
   * Actualización automática.
   */
  if (refreshTimer) {
    clearInterval(refreshTimer);
  }

  refreshTimer = setInterval(refreshDashboard, 3000);

  console.log("[TacticalVision] Dashboard ONLINE");
}

/* ============================================================
   START
   ============================================================ */

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeDashboard);
} else {
  initializeDashboard();
}

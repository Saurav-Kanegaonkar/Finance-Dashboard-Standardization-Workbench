const state = {
  data: null,
  view: "cockpit",
};

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const whole = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });

const viewRoot = document.querySelector("#viewRoot");
const kpiGrid = document.querySelector("#kpiGrid");
const tabs = document.querySelectorAll(".tab");

function formatMoney(value) {
  if (Math.abs(value) >= 1_000_000) {
    return `${money.format(value / 1_000_000)}M`;
  }
  return money.format(value);
}

function formatPct(value) {
  return `${Number(value).toFixed(1)}%`;
}

function riskClass(value) {
  if (Number(value) >= 66) return "risk-high";
  if (Number(value) >= 48) return "risk-mid";
  return "risk-low";
}

function renderKpis() {
  const { summary } = state.data;
  const metrics = [
    ["Latest net revenue", formatMoney(summary.total_revenue), `${formatPct(summary.avg_margin_pct)} average margin`],
    ["Certified KPI coverage", formatPct(summary.certified_metric_pct), `${summary.metrics} governed metrics`],
    ["Open requirements", whole.format(summary.open_requirements), `${summary.dashboards} Power BI dashboards`],
    ["SAC ready handoffs", whole.format(summary.sac_ready_handoffs), `${summary.estimated_manual_hours} monthly manual hours`],
  ];

  kpiGrid.innerHTML = metrics
    .map(
      ([label, value, note]) => `
        <article class="kpi">
          <span>${label}</span>
          <strong>${value}</strong>
          <em>${note}</em>
        </article>
      `
    )
    .join("");
}

function barList(items, valueKey, labelKey, noteKey) {
  const max = Math.max(...items.map((item) => Number(item[valueKey])));
  return `
    <div class="bar-list">
      ${items
        .map((item) => {
          const value = Number(item[valueKey]);
          const width = Math.max(6, (value / max) * 100);
          return `
            <div class="bar-row">
              <div class="bar-label">
                <b>${item[labelKey]}</b>
                <span>${item[noteKey]}</span>
              </div>
              <div class="bar-track"><span style="width:${width}%"></span></div>
              <strong>${value.toFixed(1)}</strong>
            </div>
          `;
        })
        .join("")}
    </div>
  `;
}

function table(headers, rows) {
  return `
    <div class="table-wrap">
      <table>
        <thead><tr>${headers.map((header) => `<th>${header}</th>`).join("")}</tr></thead>
        <tbody>${rows.join("")}</tbody>
      </table>
    </div>
  `;
}

function renderCockpit() {
  const { standardizationQueue, serviceLineSummary, recommendations } = state.data;
  const topQueue = standardizationQueue.slice(0, 6);
  const serviceRows = serviceLineSummary
    .slice(0, 8)
    .map(
      (row) => `
        <tr>
          <td>${row.service_line}</td>
          <td>${formatMoney(row.net_revenue)}</td>
          <td>${formatPct(row.operating_margin_pct)}</td>
          <td>${formatPct(row.denial_rate_pct)}</td>
        </tr>
      `
    );

  viewRoot.innerHTML = `
    <section class="content-grid">
      <article class="panel wide">
        <div class="panel-heading">
          <p class="eyebrow">Power BI standardization queue</p>
          <h2>Where finance reporting cleanup should start</h2>
        </div>
        ${barList(topQueue, "standardization_score", "dashboard_name", "recommended_decision")}
      </article>
      <article class="panel">
        <div class="panel-heading">
          <p class="eyebrow">Operating readout</p>
          <h2>Current finance signals</h2>
        </div>
        ${table(["Service line", "Net revenue", "Margin", "Denials"], serviceRows)}
      </article>
    </section>
    <section class="recommendation-grid">
      ${recommendations
        .map(
          (item, index) => `
            <article class="recommendation">
              <span>${String(index + 1).padStart(2, "0")}</span>
              <h3>${item.title}</h3>
              <p>${item.body}</p>
            </article>
          `
        )
        .join("")}
    </section>
  `;
}

function renderStandards() {
  const { requirementMatrix, standardizationQueue, metricCatalog } = state.data;
  const reqRows = requirementMatrix
    .slice(0, 9)
    .map(
      (row) => `
        <tr>
          <td>${row.requirement_id}</td>
          <td>${row.dashboard_name}</td>
          <td>${row.stakeholder_group}</td>
          <td><span class="pill">${row.priority}</span></td>
          <td>${row.status}</td>
          <td>${row.target_release}</td>
        </tr>
      `
    );
  const catalogRows = metricCatalog
    .filter((row) => row.certified_status !== "Certified" || row.sac_ready === "No")
    .slice(0, 8)
    .map(
      (row) => `
        <tr>
          <td>${row.metric_name}</td>
          <td>${row.service_line}</td>
          <td>${row.owner}</td>
          <td>${row.certified_status}</td>
          <td>${row.sac_ready}</td>
        </tr>
      `
    );

  viewRoot.innerHTML = `
    <section class="content-grid">
      <article class="panel wide">
        <div class="panel-heading">
          <p class="eyebrow">Requirements intake</p>
          <h2>Stakeholder requests mapped to report standards</h2>
        </div>
        ${table(["ID", "Dashboard", "Stakeholder", "Priority", "Status", "Release"], reqRows)}
      </article>
      <article class="panel">
        <div class="panel-heading">
          <p class="eyebrow">Format and governance</p>
          <h2>Lowest readiness reports</h2>
        </div>
        ${barList(standardizationQueue.slice(0, 5), "sac_gap_pct", "dashboard_name", "portfolio")}
      </article>
    </section>
    <section class="panel full">
      <div class="panel-heading">
        <p class="eyebrow">Metric catalog exceptions</p>
        <h2>KPI definitions that need owner or SAC readiness work</h2>
      </div>
      ${table(["Metric", "Service line", "Owner", "Certification", "SAC ready"], catalogRows)}
    </section>
  `;
}

function renderQuality() {
  const { qualityQueue, refreshTrend } = state.data;
  const issueRows = qualityQueue
    .slice(0, 10)
    .map(
      (row) => `
        <tr>
          <td>${row.check_id}</td>
          <td>${row.dashboard_name}</td>
          <td>${row.source_system}</td>
          <td>${row.category}</td>
          <td><span class="pill ${row.severity.toLowerCase()}">${row.severity}</span></td>
          <td>${formatPct(row.fail_rate_pct)}</td>
          <td>${row.open_days}</td>
        </tr>
      `
    );
  const trendRows = refreshTrend
    .slice(-10)
    .map(
      (row) => `
        <tr>
          <td>${row.run_date}</td>
          <td>${row.runs}</td>
          <td>${row.failed}</td>
          <td>${row.warnings}</td>
        </tr>
      `
    );

  viewRoot.innerHTML = `
    <section class="content-grid">
      <article class="panel wide">
        <div class="panel-heading">
          <p class="eyebrow">Data quality queue</p>
          <h2>Refresh and source defects blocking trusted reporting</h2>
        </div>
        ${table(["ID", "Dashboard", "Source", "Category", "Severity", "Fail rate", "Open days"], issueRows)}
      </article>
      <article class="panel">
        <div class="panel-heading">
          <p class="eyebrow">Refresh reliability</p>
          <h2>Recent run pattern</h2>
        </div>
        ${table(["Date", "Runs", "Failed", "Warnings"], trendRows)}
      </article>
    </section>
    <section class="issue-grid">
      ${qualityQueue
        .slice(0, 4)
        .map(
          (row) => `
            <article class="issue ${riskClass(row.fail_rate_pct * 3)}">
              <span>${row.category}</span>
              <h3>${row.check_name}</h3>
              <p>${row.recommended_fix}</p>
              <b>${formatPct(row.fail_rate_pct)} fail rate</b>
            </article>
          `
        )
        .join("")}
    </section>
  `;
}

function renderSac() {
  const { sacBacklog } = state.data;
  const rows = sacBacklog
    .slice(0, 12)
    .map(
      (row) => `
        <tr>
          <td>${row.handoff_id}</td>
          <td>${row.planning_version}</td>
          <td>${row.service_line}</td>
          <td>${row.dashboard_name}</td>
          <td>${formatPct(row.mapping_completeness_pct)}</td>
          <td>${row.currency_rule_documented}</td>
          <td>${row.data_access_reviewed}</td>
          <td>${row.status}</td>
        </tr>
      `
    );
  const needsWork = sacBacklog.filter((row) => row.status !== "Ready");
  const ready = sacBacklog.length - needsWork.length;

  viewRoot.innerHTML = `
    <section class="content-grid">
      <article class="panel wide">
        <div class="panel-heading">
          <p class="eyebrow">SAP Analytics Cloud handoff</p>
          <h2>Planning packets with mapping, currency, and access checks</h2>
        </div>
        ${table(["ID", "Version", "Service line", "Source report", "Mapping", "Currency", "Access", "Status"], rows)}
      </article>
      <article class="panel action-panel">
        <div class="panel-heading">
          <p class="eyebrow">Readiness split</p>
          <h2>${ready} ready, ${needsWork.length} need work</h2>
        </div>
        <div class="donut" style="--ready:${(ready / sacBacklog.length) * 360}deg">
          <strong>${formatPct((ready / sacBacklog.length) * 100)}</strong>
          <span>ready</span>
        </div>
        <p>Readiness requires mapped service line dimensions, documented currency rules, and reviewed data access groups.</p>
      </article>
    </section>
  `;
}

function render() {
  renderKpis();
  if (state.view === "cockpit") renderCockpit();
  if (state.view === "standards") renderStandards();
  if (state.view === "quality") renderQuality();
  if (state.view === "sac") renderSac();
}

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((item) => item.classList.toggle("is-active", item === tab));
    state.view = tab.dataset.view;
    render();
  });
});

fetch("analysis/outputs/app_payload.json")
  .then((response) => response.json())
  .then((payload) => {
    state.data = payload;
    render();
  })
  .catch(() => {
    viewRoot.innerHTML = `
      <article class="panel">
        <h2>Unable to load analysis payload</h2>
        <p>Run <code>python3 scripts/score_operating_data.py</code>, then start a local web server.</p>
      </article>
    `;
  });

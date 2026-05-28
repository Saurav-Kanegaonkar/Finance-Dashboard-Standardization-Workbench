import csv
import json
import random
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ANALYSIS = ROOT / "analysis"
OUTPUTS = ANALYSIS / "outputs"

RNG = random.Random(426)


SERVICE_LINES = [
    ("SL01", "Cardiology", "Acute care"),
    ("SL02", "Oncology", "Specialty care"),
    ("SL03", "Orthopedics", "Procedural"),
    ("SL04", "Emergency", "Access"),
    ("SL05", "Women's Health", "Acute care"),
    ("SL06", "Imaging", "Ancillary"),
    ("SL07", "Primary Care", "Ambulatory"),
    ("SL08", "Behavioral Health", "Ambulatory"),
]

SOURCE_SYSTEMS = [
    "Epic Resolute",
    "SAP Finance",
    "Workday Payroll",
    "Strata Planning",
    "Claims Clearinghouse",
    "Provider Master",
]

METRIC_TEMPLATES = [
    ("NET_REV", "Net revenue", "Finance", "USD", "Sum of posted net revenue after contractual adjustments.", "Actuals"),
    ("OP_MARGIN", "Operating margin", "Finance", "Percent", "Operating income divided by net revenue.", "Actuals"),
    ("LABOR_CASE", "Labor cost per case", "Finance", "USD", "Direct labor expense divided by adjusted cases.", "Actuals"),
    ("DENIAL_RATE", "Initial denial rate", "Revenue Cycle", "Percent", "Denied claims divided by submitted claims.", "Claims"),
    ("AR_DAYS", "A/R days", "Revenue Cycle", "Days", "Net accounts receivable divided by average daily net revenue.", "Claims"),
    ("SUPPLY_CASE", "Supply cost per case", "Finance", "USD", "Supply expense divided by adjusted cases.", "Actuals"),
    ("BUDGET_VAR", "Budget variance", "FP&A", "Percent", "Actual expense minus budget, divided by budget.", "Planning"),
    ("FORECAST_ACC", "Forecast accuracy", "FP&A", "Percent", "One minus absolute forecast error divided by actuals.", "Planning"),
    ("CASE_MIX", "Case mix index", "Operations", "Index", "Weighted clinical acuity index used for finance normalization.", "Clinical"),
    ("VOLUME", "Adjusted cases", "Operations", "Count", "Inpatient and equivalent outpatient case volume.", "Clinical"),
]

DASHBOARD_TEMPLATES = [
    ("FIN-001", "Monthly close executive packet", "Finance", "Executive"),
    ("FIN-002", "Service line margin review", "Finance", "Director"),
    ("FIN-003", "Labor productivity monitor", "Finance", "Manager"),
    ("FIN-004", "Supply cost variance board", "Finance", "Manager"),
    ("RCM-001", "Denials and A/R command center", "Revenue Cycle", "Director"),
    ("RCM-002", "Payer mix and reimbursement report", "Revenue Cycle", "Manager"),
    ("OPS-001", "Volume and capacity dashboard", "Operations", "Director"),
    ("OPS-002", "Ancillary utilization scorecard", "Operations", "Manager"),
    ("FPA-001", "Forecast version bridge", "FP&A", "Executive"),
    ("FPA-002", "Budget owner review packet", "FP&A", "Director"),
    ("GOV-001", "Metric certification tracker", "Analytics", "Manager"),
    ("GOV-002", "Dashboard adoption and intake queue", "Analytics", "Director"),
]

REQUIREMENT_THEMES = [
    "standardize service line filter behavior",
    "replace Excel reconciliation tab",
    "show budget to actual variance by cost center",
    "add payer drill through for margin movement",
    "create certified KPI definition tooltip",
    "publish monthly close exception list",
    "align Power BI page titles to finance taxonomy",
    "map report output to SAC planning version",
    "show refresh status and source owner",
    "add security group and data access notes",
]

QUALITY_CHECKS = [
    ("Missing cost center mapping", "Mapping", 0.18),
    ("Late ledger refresh", "Freshness", 0.22),
    ("Payer code not aligned to finance hierarchy", "Conformance", 0.15),
    ("Metric definition drift", "Definition", 0.19),
    ("Duplicate monthly close row", "Completeness", 0.10),
    ("Manual adjustment not documented", "Auditability", 0.16),
]


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def pct(value):
    return round(value, 1)


def money(value):
    return int(round(value, 0))


def build_data():
    DATA.mkdir(exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)

    metric_rows = []
    for service_id, service_line, family in SERVICE_LINES:
        for code, metric, domain, unit, definition, grain in METRIC_TEMPLATES:
            metric_id = f"{service_id}-{code}"
            certified = RNG.random() > 0.18
            metric_rows.append(
                {
                    "metric_id": metric_id,
                    "metric_name": metric,
                    "service_line": service_line,
                    "domain": domain,
                    "unit": unit,
                    "grain": grain,
                    "definition": definition,
                    "owner": RNG.choice(["Finance Analytics", "FP&A", "Revenue Cycle", "Operations Analytics"]),
                    "power_bi_measure": f"[{service_line} {metric}]",
                    "certified_status": "Certified" if certified else RNG.choice(["Draft", "Needs owner", "Conflicting logic"]),
                    "sac_ready": "Yes" if certified and RNG.random() > 0.26 else "No",
                }
            )

    dashboard_rows = []
    for dashboard_id, dashboard_name, portfolio, audience in DASHBOARD_TEMPLATES:
        metric_count = RNG.randint(7, 15)
        certified_pct = RNG.uniform(0.52, 0.94)
        format_score = RNG.uniform(58, 96)
        manual_hours = RNG.randint(3, 18)
        refresh_sla_pct = RNG.uniform(0.76, 0.99)
        stakeholder_count = RNG.randint(5, 22)
        sac_coverage_pct = RNG.uniform(0.28, 0.91) if portfolio in ["Finance", "FP&A"] else RNG.uniform(0.10, 0.55)
        dashboard_rows.append(
            {
                "dashboard_id": dashboard_id,
                "dashboard_name": dashboard_name,
                "portfolio": portfolio,
                "audience": audience,
                "metric_count": metric_count,
                "certified_metric_pct": pct(certified_pct * 100),
                "format_score": pct(format_score),
                "manual_hours_monthly": manual_hours,
                "refresh_sla_pct": pct(refresh_sla_pct * 100),
                "stakeholder_count": stakeholder_count,
                "sac_coverage_pct": pct(sac_coverage_pct * 100),
                "owner": RNG.choice(["Finance BI", "Enterprise Analytics", "FP&A Reporting", "Revenue Cycle Analytics"]),
            }
        )

    actual_rows = []
    start_month = date(2025, 7, 1)
    for month_offset in range(12):
        period = start_month + timedelta(days=31 * month_offset)
        period_label = period.replace(day=1).isoformat()
        for service_id, service_line, family in SERVICE_LINES:
            volume = RNG.randint(1800, 8600)
            net_revenue = volume * RNG.uniform(2200, 8200)
            expense = net_revenue * RNG.uniform(0.82, 1.08)
            budget = expense * RNG.uniform(0.94, 1.06)
            denied_claims = RNG.randint(80, 900)
            claims = denied_claims / RNG.uniform(0.045, 0.14)
            actual_rows.append(
                {
                    "period": period_label,
                    "service_line": service_line,
                    "net_revenue": money(net_revenue),
                    "operating_expense": money(expense),
                    "operating_margin_pct": pct((net_revenue - expense) / net_revenue * 100),
                    "budget_variance_pct": pct((expense - budget) / budget * 100),
                    "adjusted_cases": volume,
                    "labor_cost_per_case": money(RNG.uniform(650, 2100)),
                    "denial_rate_pct": pct(denied_claims / claims * 100),
                    "forecast_accuracy_pct": pct(RNG.uniform(82, 98)),
                }
            )

    requirement_rows = []
    for idx in range(1, 55):
        dashboard = RNG.choice(dashboard_rows)
        theme = RNG.choice(REQUIREMENT_THEMES)
        priority = RNG.choice(["High", "High", "Medium", "Medium", "Watch"])
        status = RNG.choice(["Discovery", "Design", "Build", "UAT", "Ready for release"])
        complexity = RNG.randint(1, 5)
        impact = RNG.randint(55, 98)
        requirement_rows.append(
            {
                "requirement_id": f"REQ-{idx:03d}",
                "dashboard_id": dashboard["dashboard_id"],
                "dashboard_name": dashboard["dashboard_name"],
                "stakeholder_group": RNG.choice(["Finance directors", "FP&A partners", "Revenue cycle leaders", "Operations executives"]),
                "requirement": theme,
                "priority": priority,
                "status": status,
                "complexity": complexity,
                "business_impact_score": impact,
                "mapped_metric_id": RNG.choice(metric_rows)["metric_id"],
                "target_release": RNG.choice(["2026-06", "2026-07", "2026-08", "2026-09"]),
            }
        )

    refresh_rows = []
    today = date(2026, 5, 1)
    for day in range(28):
        run_date = today + timedelta(days=day)
        for dashboard in dashboard_rows:
            failed = RNG.random() > float(dashboard["refresh_sla_pct"]) / 100
            duration = RNG.randint(14, 92) + (35 if failed else 0)
            refresh_rows.append(
                {
                    "run_date": run_date.isoformat(),
                    "dashboard_id": dashboard["dashboard_id"],
                    "dashboard_name": dashboard["dashboard_name"],
                    "source_system": RNG.choice(SOURCE_SYSTEMS),
                    "status": "Failed" if failed else RNG.choice(["Succeeded", "Succeeded", "Succeeded", "Warning"]),
                    "duration_minutes": duration,
                    "rows_processed": RNG.randint(18000, 980000),
                    "defect_count": RNG.randint(0, 4) if not failed else RNG.randint(3, 12),
                }
            )

    quality_rows = []
    for idx in range(1, 97):
        dashboard = RNG.choice(dashboard_rows)
        check_name, category, base_rate = RNG.choice(QUALITY_CHECKS)
        fail_rate = min(0.44, max(0.02, RNG.gauss(base_rate, 0.055)))
        severity = "Critical" if fail_rate > 0.27 else "High" if fail_rate > 0.18 else "Medium" if fail_rate > 0.10 else "Low"
        quality_rows.append(
            {
                "check_id": f"QC-{idx:03d}",
                "dashboard_id": dashboard["dashboard_id"],
                "dashboard_name": dashboard["dashboard_name"],
                "source_system": RNG.choice(SOURCE_SYSTEMS),
                "check_name": check_name,
                "category": category,
                "fail_rate_pct": pct(fail_rate * 100),
                "severity": severity,
                "open_days": RNG.randint(1, 42),
                "recommended_fix": RNG.choice(
                    [
                        "assign source owner and certify mapping",
                        "add refresh alert and retry rule",
                        "lock metric definition in catalog",
                        "route exception to monthly close review",
                        "document adjustment source and approver",
                    ]
                ),
            }
        )

    sac_rows = []
    for idx in range(1, 25):
        dashboard = RNG.choice([row for row in dashboard_rows if row["portfolio"] in ["Finance", "FP&A"]])
        service_line = RNG.choice(SERVICE_LINES)[1]
        completeness = RNG.uniform(0.45, 0.96)
        has_currency = RNG.random() > 0.28
        has_access = RNG.random() > 0.22
        status = "Ready" if completeness > 0.80 and has_currency and has_access else RNG.choice(["Needs mapping", "Needs access", "Needs version owner"])
        sac_rows.append(
            {
                "handoff_id": f"SAC-{idx:03d}",
                "dashboard_id": dashboard["dashboard_id"],
                "dashboard_name": dashboard["dashboard_name"],
                "planning_version": RNG.choice(["Budget 2027", "Forecast Q3", "Forecast Q4", "Board scenario"]),
                "service_line": service_line,
                "mapping_completeness_pct": pct(completeness * 100),
                "currency_rule_documented": "Yes" if has_currency else "No",
                "data_access_reviewed": "Yes" if has_access else "No",
                "status": status,
                "next_owner": RNG.choice(["FP&A", "Finance BI", "SAC admin", "Service line finance"]),
            }
        )

    return metric_rows, dashboard_rows, actual_rows, requirement_rows, refresh_rows, quality_rows, sac_rows


def score_and_write():
    metric_rows, dashboard_rows, actual_rows, requirement_rows, refresh_rows, quality_rows, sac_rows = build_data()

    write_csv(
        DATA / "metric_definitions.csv",
        metric_rows,
        [
            "metric_id",
            "metric_name",
            "service_line",
            "domain",
            "unit",
            "grain",
            "definition",
            "owner",
            "power_bi_measure",
            "certified_status",
            "sac_ready",
        ],
    )
    write_csv(DATA / "dashboard_inventory.csv", dashboard_rows, list(dashboard_rows[0].keys()))
    write_csv(DATA / "finance_actuals.csv", actual_rows, list(actual_rows[0].keys()))
    write_csv(DATA / "stakeholder_requirements.csv", requirement_rows, list(requirement_rows[0].keys()))
    write_csv(DATA / "refresh_runs.csv", refresh_rows, list(refresh_rows[0].keys()))
    write_csv(DATA / "data_quality_checks.csv", quality_rows, list(quality_rows[0].keys()))
    write_csv(DATA / "sac_planning_requests.csv", sac_rows, list(sac_rows[0].keys()))

    reqs_by_dashboard = defaultdict(list)
    refresh_by_dashboard = defaultdict(list)
    quality_by_dashboard = defaultdict(list)
    sac_by_dashboard = defaultdict(list)
    for row in requirement_rows:
        reqs_by_dashboard[row["dashboard_id"]].append(row)
    for row in refresh_rows:
        refresh_by_dashboard[row["dashboard_id"]].append(row)
    for row in quality_rows:
        quality_by_dashboard[row["dashboard_id"]].append(row)
    for row in sac_rows:
        sac_by_dashboard[row["dashboard_id"]].append(row)

    standardization_queue = []
    for row in dashboard_rows:
        dashboard_id = row["dashboard_id"]
        open_high_reqs = sum(1 for req in reqs_by_dashboard[dashboard_id] if req["priority"] == "High" and req["status"] != "Ready for release")
        failed_refreshes = sum(1 for run in refresh_by_dashboard[dashboard_id] if run["status"] == "Failed")
        quality_pressure = sum(float(check["fail_rate_pct"]) for check in quality_by_dashboard[dashboard_id]) / max(1, len(quality_by_dashboard[dashboard_id]))
        sac_gap = 100 - float(row["sac_coverage_pct"])
        certified_gap = 100 - float(row["certified_metric_pct"])
        format_gap = 100 - float(row["format_score"])
        score = (
            certified_gap * 0.24
            + format_gap * 0.18
            + failed_refreshes * 4.2
            + quality_pressure * 0.82
            + int(row["manual_hours_monthly"]) * 1.1
            + open_high_reqs * 5.0
            + sac_gap * 0.10
        )
        if score >= 66:
            decision = "Standardize next"
        elif score >= 48:
            decision = "Schedule requirements review"
        else:
            decision = "Monitor"
        standardization_queue.append(
            {
                "dashboard_id": dashboard_id,
                "dashboard_name": row["dashboard_name"],
                "portfolio": row["portfolio"],
                "standardization_score": pct(score),
                "certified_metric_pct": row["certified_metric_pct"],
                "format_score": row["format_score"],
                "failed_refreshes": failed_refreshes,
                "open_high_requirements": open_high_reqs,
                "manual_hours_monthly": row["manual_hours_monthly"],
                "sac_gap_pct": pct(sac_gap),
                "recommended_decision": decision,
            }
        )
    standardization_queue.sort(key=lambda item: item["standardization_score"], reverse=True)

    quality_queue = sorted(
        quality_rows,
        key=lambda item: (["Low", "Medium", "High", "Critical"].index(item["severity"]), float(item["fail_rate_pct"]), item["open_days"]),
        reverse=True,
    )

    req_matrix = sorted(
        requirement_rows,
        key=lambda item: (item["priority"] == "High", item["business_impact_score"], -item["complexity"]),
        reverse=True,
    )

    sac_queue = sorted(
        sac_rows,
        key=lambda item: (item["status"] == "Ready", float(item["mapping_completeness_pct"])),
        reverse=True,
    )

    write_csv(OUTPUTS / "standardization_queue.csv", standardization_queue, list(standardization_queue[0].keys()))
    write_csv(OUTPUTS / "data_quality_queue.csv", quality_queue, list(quality_queue[0].keys()))
    write_csv(OUTPUTS / "stakeholder_requirement_matrix.csv", req_matrix, list(req_matrix[0].keys()))
    write_csv(OUTPUTS / "sac_planning_handoff.csv", sac_queue, list(sac_queue[0].keys()))

    latest_actuals = [row for row in actual_rows if row["period"] == max(item["period"] for item in actual_rows)]
    total_revenue = sum(int(row["net_revenue"]) for row in latest_actuals)
    avg_margin = sum(float(row["operating_margin_pct"]) for row in latest_actuals) / len(latest_actuals)
    avg_forecast = sum(float(row["forecast_accuracy_pct"]) for row in latest_actuals) / len(latest_actuals)
    certified_metrics = sum(1 for row in metric_rows if row["certified_status"] == "Certified")
    sac_ready = sum(1 for row in sac_rows if row["status"] == "Ready")
    refresh_failures = sum(1 for row in refresh_rows if row["status"] == "Failed")
    high_quality = sum(1 for row in quality_rows if row["severity"] in ["High", "Critical"])

    service_line_summary = []
    for row in latest_actuals:
        service_line_summary.append(
            {
                "service_line": row["service_line"],
                "net_revenue": int(row["net_revenue"]),
                "operating_margin_pct": float(row["operating_margin_pct"]),
                "budget_variance_pct": float(row["budget_variance_pct"]),
                "denial_rate_pct": float(row["denial_rate_pct"]),
                "forecast_accuracy_pct": float(row["forecast_accuracy_pct"]),
            }
        )
    service_line_summary.sort(key=lambda item: item["net_revenue"], reverse=True)

    refresh_trend = []
    by_day = defaultdict(lambda: {"runs": 0, "failed": 0, "warnings": 0})
    for row in refresh_rows:
        bucket = by_day[row["run_date"]]
        bucket["runs"] += 1
        bucket["failed"] += 1 if row["status"] == "Failed" else 0
        bucket["warnings"] += 1 if row["status"] == "Warning" else 0
    for run_date, bucket in sorted(by_day.items()):
        refresh_trend.append({"run_date": run_date, **bucket})

    payload = {
        "summary": {
            "total_revenue": total_revenue,
            "avg_margin_pct": pct(avg_margin),
            "avg_forecast_accuracy_pct": pct(avg_forecast),
            "dashboards": len(dashboard_rows),
            "metrics": len(metric_rows),
            "certified_metric_pct": pct(certified_metrics / len(metric_rows) * 100),
            "open_requirements": sum(1 for row in requirement_rows if row["status"] != "Ready for release"),
            "refresh_failures": refresh_failures,
            "high_quality_issues": high_quality,
            "sac_ready_handoffs": sac_ready,
            "estimated_manual_hours": sum(int(row["manual_hours_monthly"]) for row in dashboard_rows),
        },
        "standardizationQueue": standardization_queue,
        "requirementMatrix": req_matrix,
        "qualityQueue": quality_queue,
        "sacBacklog": sac_queue,
        "serviceLineSummary": service_line_summary,
        "dashboardInventory": dashboard_rows,
        "metricCatalog": metric_rows,
        "refreshTrend": refresh_trend,
        "recommendations": [
            {
                "title": "Certify shared finance KPIs first",
                "body": "Focus metric owner reviews on the reports with low certified metric coverage and high stakeholder demand.",
            },
            {
                "title": "Move recurring Excel tabs into monitored Power BI pages",
                "body": "The highest standardization scores combine manual monthly effort, refresh failures, and open high-priority requirements.",
            },
            {
                "title": "Package SAC handoffs with access and currency rules",
                "body": "Planning requests are only ready when mappings, currency logic, and data access reviews are documented together.",
            },
        ],
    }

    (OUTPUTS / "app_payload.json").write_text(json.dumps(payload, indent=2))

    (ANALYSIS / "executive_findings.md").write_text(
        "\n".join(
            [
                "# Executive Findings",
                "",
                "## What I analyzed",
                "",
                f"I generated and scored {len(dashboard_rows)} Power BI finance dashboards, {len(metric_rows)} KPI definitions, "
                f"{len(requirement_rows)} stakeholder requirements, {len(refresh_rows)} refresh runs, "
                f"{len(quality_rows)} data quality checks, and {len(sac_rows)} SAP Analytics Cloud planning handoff records.",
                "",
                "## Findings",
                "",
                f"- Highest standardization priority: {standardization_queue[0]['dashboard_name']} with a score of {standardization_queue[0]['standardization_score']}.",
                f"- Certified metric coverage is {payload['summary']['certified_metric_pct']} percent across the catalog.",
                f"- There are {payload['summary']['refresh_failures']} failed refreshes and {payload['summary']['high_quality_issues']} high or critical data quality issues in the modeled period.",
                f"- {payload['summary']['sac_ready_handoffs']} SAC planning handoffs are ready without additional mapping, access, or currency-rule work.",
                "",
                "## Recommendation",
                "",
                "Use the standardization queue to sequence Power BI cleanup work, then review requirements, refresh defects, and SAC handoff gaps from the same operating model.",
            ]
        )
        + "\n"
    )

    (ANALYSIS / "analysis_plan.md").write_text(
        "\n".join(
            [
                "# Analysis Plan",
                "",
                "1. Generate healthcare finance reporting data at dashboard, metric, requirement, refresh, quality, actuals, and SAC handoff grains.",
                "2. Score dashboard standardization need using certified KPI coverage, visual format score, refresh failures, quality pressure, manual reporting effort, high-priority requirements, and SAC coverage gaps.",
                "3. Rank requirements by stakeholder priority, business impact, and complexity.",
                "4. Rank quality issues by severity, failure rate, and age.",
                "5. Package the outputs into an application payload for the static reporting workbench.",
            ]
        )
        + "\n"
    )

    (ANALYSIS / "sql_checks.sql").write_text(
        "\n".join(
            [
                "-- SQL-style checks for a healthcare finance reporting standardization workbench.",
                "",
                "-- Find dashboards with high manual effort and low certified metric coverage.",
                "select dashboard_id, dashboard_name, certified_metric_pct, manual_hours_monthly",
                "from dashboard_inventory",
                "where certified_metric_pct < 70 and manual_hours_monthly >= 10",
                "order by manual_hours_monthly desc;",
                "",
                "-- Identify stale or failed refreshes by source system.",
                "select source_system, status, count(*) as run_count, sum(defect_count) as defects",
                "from refresh_runs",
                "where status in ('Failed', 'Warning')",
                "group by source_system, status",
                "order by defects desc;",
                "",
                "-- Locate SAC handoffs that need mapping, access, or currency-rule work.",
                "select handoff_id, dashboard_name, planning_version, service_line, status",
                "from sac_planning_requests",
                "where status <> 'Ready'",
                "order by mapping_completeness_pct asc;",
            ]
        )
        + "\n"
    )

    (DATA / "README.md").write_text(
        "\n".join(
            [
                "# Data Notes",
                "",
                "All project data is synthetic and generated by `scripts/score_operating_data.py`.",
                "",
                "The synthetic model is shaped like healthcare finance reporting work: service lines, payer and revenue cycle signals, monthly financial actuals, Power BI dashboard inventory, KPI definitions, stakeholder requirements, refresh runs, data quality checks, and SAP Analytics Cloud planning handoffs.",
                "",
                "The data is not real company performance data. It is designed to make the reporting workflow realistic enough to discuss in an interview.",
                "",
                "Key generation assumptions:",
                "",
                "- Service lines use common healthcare operating categories such as Cardiology, Oncology, Emergency, Imaging, and Primary Care.",
                "- Financial actuals vary by volume, net revenue, expense, budget variance, denial rate, and forecast accuracy.",
                "- Dashboard standardization risk increases when certified metric coverage is low, format scores are weak, refresh failures are present, manual monthly effort is high, stakeholder requirements are unresolved, and SAC coverage is incomplete.",
                "- SAP Analytics Cloud handoffs require mapping completeness, currency rules, and access review before they are considered ready.",
            ]
        )
        + "\n"
    )

    (ROOT / "data_dictionary.md").write_text(
        "\n".join(
            [
                "# Data Dictionary",
                "",
                "| File | Grain | Purpose |",
                "| --- | --- | --- |",
                "| `data/dashboard_inventory.csv` | Power BI dashboard | Dashboard ownership, audience, certified metric coverage, format score, manual effort, refresh SLA, and SAC coverage. |",
                "| `data/metric_definitions.csv` | KPI by service line | Metric owner, definition, unit, grain, Power BI measure label, certification status, and SAC readiness. |",
                "| `data/finance_actuals.csv` | Month by service line | Synthetic monthly finance outcomes used for cockpit KPIs and service line comparison. |",
                "| `data/stakeholder_requirements.csv` | Requirement | Finance and business stakeholder requests mapped to dashboards, metrics, priority, status, impact, and release month. |",
                "| `data/refresh_runs.csv` | Dashboard refresh run | Source system, status, duration, row volume, and defects for recurring report reliability checks. |",
                "| `data/data_quality_checks.csv` | Quality check | Quality issue category, failure rate, severity, open days, and recommended fix. |",
                "| `data/sac_planning_requests.csv` | SAC planning handoff | Planning version, service line, mapping completeness, currency rule, access review, status, and next owner. |",
                "| `analysis/outputs/app_payload.json` | App payload | Static JSON used by the interactive workbench. |",
                "| `analysis/outputs/standardization_queue.csv` | Dashboard | Ranked Power BI dashboard standardization priorities. |",
                "| `analysis/outputs/stakeholder_requirement_matrix.csv` | Requirement | Requirements sorted for stakeholder review. |",
                "| `analysis/outputs/data_quality_queue.csv` | Quality check | Data quality and refresh defects sorted by severity and age. |",
                "| `analysis/outputs/sac_planning_handoff.csv` | SAC handoff | Planning handoff records sorted by readiness. |",
            ]
        )
        + "\n"
    )

    (ROOT / "STATUS.md").write_text(
        "\n".join(
            [
                "# Status",
                "",
                "- Project: Finance Dashboard Standardization Workbench",
                "- GitHub: https://github.com/Saurav-Kanegaonkar/Finance-Dashboard-Standardization-Workbench",
                "- Status: upgraded through the Portfolio Artifact Upgrade Workflow",
                "- Artifact type: healthcare finance Power BI reporting standardization workbench",
            ]
        )
        + "\n"
    )

    print(f"Generated {len(dashboard_rows)} dashboards, {len(metric_rows)} metrics, and {len(requirement_rows)} requirements.")
    print(f"Top standardization priority: {standardization_queue[0]['dashboard_name']} ({standardization_queue[0]['standardization_score']})")
    print(f"Certified metric coverage: {payload['summary']['certified_metric_pct']}%")


if __name__ == "__main__":
    score_and_write()

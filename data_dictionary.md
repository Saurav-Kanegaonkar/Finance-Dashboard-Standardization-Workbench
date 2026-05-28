# Data Dictionary

| File | Grain | Purpose |
| --- | --- | --- |
| `data/dashboard_inventory.csv` | Power BI dashboard | Dashboard ownership, audience, certified metric coverage, format score, manual effort, refresh SLA, and SAC coverage. |
| `data/metric_definitions.csv` | KPI by service line | Metric owner, definition, unit, grain, Power BI measure label, certification status, and SAC readiness. |
| `data/finance_actuals.csv` | Month by service line | Synthetic monthly finance outcomes used for cockpit KPIs and service line comparison. |
| `data/stakeholder_requirements.csv` | Requirement | Finance and business stakeholder requests mapped to dashboards, metrics, priority, status, impact, and release month. |
| `data/refresh_runs.csv` | Dashboard refresh run | Source system, status, duration, row volume, and defects for recurring report reliability checks. |
| `data/data_quality_checks.csv` | Quality check | Quality issue category, failure rate, severity, open days, and recommended fix. |
| `data/sac_planning_requests.csv` | SAC planning handoff | Planning version, service line, mapping completeness, currency rule, access review, status, and next owner. |
| `analysis/outputs/app_payload.json` | App payload | Static JSON used by the interactive workbench. |
| `analysis/outputs/standardization_queue.csv` | Dashboard | Ranked Power BI dashboard standardization priorities. |
| `analysis/outputs/stakeholder_requirement_matrix.csv` | Requirement | Requirements sorted for stakeholder review. |
| `analysis/outputs/data_quality_queue.csv` | Quality check | Data quality and refresh defects sorted by severity and age. |
| `analysis/outputs/sac_planning_handoff.csv` | SAC handoff | Planning handoff records sorted by readiness. |

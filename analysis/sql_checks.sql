-- SQL-style checks for a healthcare finance reporting standardization workbench.

-- Find dashboards with high manual effort and low certified metric coverage.
select dashboard_id, dashboard_name, certified_metric_pct, manual_hours_monthly
from dashboard_inventory
where certified_metric_pct < 70 and manual_hours_monthly >= 10
order by manual_hours_monthly desc;

-- Identify stale or failed refreshes by source system.
select source_system, status, count(*) as run_count, sum(defect_count) as defects
from refresh_runs
where status in ('Failed', 'Warning')
group by source_system, status
order by defects desc;

-- Locate SAC handoffs that need mapping, access, or currency-rule work.
select handoff_id, dashboard_name, planning_version, service_line, status
from sac_planning_requests
where status <> 'Ready'
order by mapping_completeness_pct asc;

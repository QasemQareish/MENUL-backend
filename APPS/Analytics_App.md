# Analytics App

## 1. Overview
**Purpose:** Analytical platform for operational, financial, and customer intelligence across all apps.

**Main responsibilities:**
- Ingest domain events from operational services.
- Model curated dimensional marts.
- Serve dashboards and scheduled reports.
- Provide forecasting and anomaly detection outputs.

## 2. Core Features
- Near-real-time sales and order SLA dashboards.
- Menu performance and contribution margin analysis.
- Branch comparatives and cohort trends.
- Inventory variance impact analysis.
- Marketing campaign attribution views.

## 3. Backend Design
### Services/modules
- `event-ingestion-service`
- `transformation-pipelines`
- `metrics-api`
- `report-scheduler`

### Business logic breakdown
- Bronze/Silver/Gold model pipeline.
- Late-arriving event handling with watermark strategy.
- Metric definitions versioned to prevent silent report drift.

### API endpoints (examples)
- `GET /v1/analytics/kpis/daily-sales`
- `GET /v1/analytics/kpis/kitchen-sla`
- `GET /v1/analytics/reports/menu-performance`
- `POST /v1/analytics/reports/schedule`

## 4. Database Design
### Tables
- `raw_events(event_id, tenant_id, event_type, payload_json, occurred_at, ingested_at)`
- `fact_orders(order_id, tenant_id, branch_id, opened_at, closed_at, total_amount, payment_status)`
- `fact_order_items(order_item_id, tenant_id, item_id, kitchen_id, qty, unit_price, status_times_json)`
- `dim_branch(branch_id, tenant_id, branch_name, region, opened_date)`
- `dim_item(item_id, tenant_id, item_name, category_name, kitchen_name)`
- `report_jobs(id, tenant_id, report_type, schedule_cron, recipients_json, status)`

### Relationships
- fact tables join dims by surrogate keys.

### Indexes
- partition `raw_events` by date.
- index `fact_orders(tenant_id, closed_at)`.
- index `fact_order_items(tenant_id, item_id, closed_date)`.

### Scaling considerations
- Columnar warehouse for analytical workloads.
- Incremental transforms and backfill orchestration.

## 5. UI/UX Specification
### Screens
- Executive Overview.
- Sales & Orders Dashboard.
- Kitchen SLA Dashboard.
- Menu Performance Explorer.
- Scheduled Reports Center.

### Layout/components
- Filter ribbon (tenant, branch, date range, channel).
- Drill-through charts with row-level export.

### Interactions
- Save custom dashboard presets per role.
- Alert subscriptions for threshold breaches.

## 6. User Roles (per app)
- Owner, Admin, Branch Manager, Analyst.

## 7. Data Flow
- Apps publish events -> ingestion -> warehouse transforms -> metrics API.
- Dashboards query curated marts; no direct OLTP dependencies.

## 8. Edge Cases
- Missing events from transient broker outage.
- Duplicate events due to producer retries.
- Metric definition changes affecting historical comparability.

## 9. Performance Considerations
- Pre-aggregated daily/hourly summary tables.
- Query result cache for common dashboard slices.
- Data freshness SLAs per metric category (real-time vs daily batch).

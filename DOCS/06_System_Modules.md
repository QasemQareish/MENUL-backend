# 06) System Modules

## 1) POS Module
- **Responsibilities:** cart management, tax/discount pricing, payment orchestration, receipt generation, shift controls.
- **Inputs:** menu snapshots, pricing rules, payment intents, customer identifiers.
- **Outputs:** completed sales transactions, payment records, fiscal receipts, event stream messages.
- **Dependencies:** Menu Builder, OMS, Payments adapter, Tax engine, Sync service.

## 2) Orders Module (OMS)
- **Responsibilities:** order lifecycle, status transitions, kitchen routing, fulfillment SLA tracking.
- **Inputs:** POS orders, app/web orders, kitchen updates.
- **Outputs:** order states, kitchen tickets, customer notifications.
- **Dependencies:** POS, Kitchen display service, Notification service.

## 3) Inventory Module
- **Responsibilities:** stock ledger, SKU/batch tracking, recipe consumption, variance detection, procurement workflows.
- **Inputs:** sales events, goods receipt, manual adjustments.
- **Outputs:** stock balances, replenishment alerts, COGS metrics.
- **Dependencies:** OMS/POS events, Vendor management, Analytics pipeline.

## 4) Menu Builder Module
- **Responsibilities:** item/catalog management, combos, variants, availability windows, localization.
- **Inputs:** product metadata, pricing rules, regional taxes.
- **Outputs:** versioned menu artifacts and publish events.
- **Dependencies:** Inventory, Tax engine, Tenant branding/localization.

## 5) CRM Module
- **Responsibilities:** customer profiles, segmentation attributes, loyalty wallet, consent tracking.
- **Inputs:** order history, channel interactions, profile updates.
- **Outputs:** segment memberships, loyalty updates, lifecycle scores.
- **Dependencies:** OMS, Marketing engine, Analytics.

## 6) Marketing Module
- **Responsibilities:** campaign creation, audience targeting, channel delivery, attribution.
- **Inputs:** segments, templates, budgets, schedule.
- **Outputs:** sends, engagement metrics, conversion events.
- **Dependencies:** CRM, Notification connectors, Analytics.

## 7) Analytics Module
- **Responsibilities:** KPI computation, OLAP-style querying, anomaly detection feeds.
- **Inputs:** transactional + operational events.
- **Outputs:** dashboards, scheduled reports, AI feature tables.
- **Dependencies:** Event bus, Data warehouse/lakehouse.

## 8) Admin Panel Module
- **Responsibilities:** tenant administration, role governance, configuration policies, audit review.
- **Inputs:** tenant config requests, policy definitions.
- **Outputs:** applied settings, access policies, audit artifacts.
- **Dependencies:** Identity/RBAC, Tenant config service, observability tools.

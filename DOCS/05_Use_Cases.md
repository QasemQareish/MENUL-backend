# 05) Use Cases

## UC-01 POS Checkout
- **Actors:** Cashier, Customer
- **Preconditions:** Shift open, terminal authenticated, menu synchronized.
- **Main Flow:** create cart -> apply discounts -> collect payment -> issue receipt -> emit events.
- **Alternate Flows:** partial payment, payment failure retry, offline capture.
- **Postconditions:** order committed, inventory deduction queued, CRM event recorded.

## UC-02 Kitchen Execution
- **Actors:** Kitchen Staff, Manager
- **Main Flow:** receive routed tickets -> accept -> cook -> ready -> handoff.
- **Alternate Flows:** out-of-stock substitution, item cancellation.

## UC-03 Inventory Replenishment
- **Actors:** Manager
- **Main Flow:** detect low stock -> create purchase request -> receive goods -> reconcile variance.

## UC-04 Campaign Launch
- **Actors:** Marketer
- **Main Flow:** define segment -> set channel/template -> schedule -> monitor conversion.

## UC-05 Tenant Onboarding
- **Actors:** Platform Admin, Tenant Owner
- **Main Flow:** tenant provisioning -> tax/currency setup -> branding -> role seeding -> go-live checklist.

## UC-06 Offline-to-Online Recovery
- **Actors:** Cashier, Sync Service
- **Main Flow:** capture local transactions -> reconnect -> replay idempotently -> resolve conflicts.

## UC-07 Multi-Branch Reporting
- **Actors:** Owner, Analyst
- **Main Flow:** query KPI dashboards -> drill down by branch/daypart/category -> export insights.

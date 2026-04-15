# Inventory App

## 1. Overview
**Purpose:** Ingredient and stock control service with branch-level visibility and depletion logic tied to orders.

**Main responsibilities:**
- Track current stock by ingredient/location.
- Record stock movements (purchase, transfer, waste, correction).
- Map recipes to menu items for consumption calculations.
- Alert low-stock and stockout risk.

## 2. Core Features
- Ingredient master data and units conversion.
- Goods receiving with supplier references.
- Inter-branch transfer workflow.
- Recipe/BOM management.
- Auto-decrement based on served items.
- Variance and wastage reporting.

## 3. Backend Design
### Services/modules
- `stock-ledger-service`
- `recipe-service`
- `replenishment-service`
- `alerting-service`

### Business logic breakdown
- Ledger is immutable; on-hand stock derived from movement sum.
- Order consumption event maps item->recipe->ingredient decrement.
- Negative stock policy configurable (strict block vs warning).

### API endpoints (examples)
- `POST /v1/inventory/ingredients`
- `POST /v1/inventory/movements`
- `POST /v1/inventory/recipes`
- `GET /v1/inventory/stock-levels?branch_id=...`
- `GET /v1/inventory/alerts/low-stock`

## 4. Database Design
### Tables
- `ingredients(id, tenant_id, name, base_unit, category, is_active)`
- `stock_locations(id, tenant_id, branch_id, name, type)`
- `stock_ledger(id, tenant_id, ingredient_id, location_id, movement_type, quantity_delta, unit_cost, ref_type, ref_id, created_at)`
- `recipes(id, tenant_id, menu_item_id, version, active)`
- `recipe_lines(id, recipe_id, ingredient_id, quantity, unit)`
- `reorder_rules(id, tenant_id, branch_id, ingredient_id, min_qty, target_qty)`

### Relationships
- recipe 1..* recipe_lines.
- ingredient 1..* stock_ledger lines.

### Indexes
- index `stock_ledger(tenant_id, ingredient_id, created_at DESC)`.
- unique `(tenant_id, branch_id, ingredient_id)` for reorder rules.

### Scaling considerations
- Partition ledger by month/tenant.
- Materialized current stock view refreshed incrementally.

## 5. UI/UX Specification
### Screens
- Ingredient Catalog.
- Stock Overview by branch/location.
- Movement Entry (receive/transfer/waste).
- Recipe Builder.
- Reorder Alerts.

### Layout/components
- Spreadsheet-like movement entry grid.
- Recipe ingredient table with unit converter.

### Interactions
- Inline warning when projected stock after save < threshold.
- Movement forms enforce reference types for traceability.

## 6. User Roles (per app)
- Owner, Branch Manager, Kitchen Manager, Procurement/Inventory Clerk.

## 7. Data Flow
- Orders emits `order.item.served` -> Inventory consumes -> writes ledger decrement.
- Inventory emits `inventory.low_stock` -> Admin/Marketing may react (e.g., hide items).

## 8. Edge Cases
- Late cancellation after consumption posted.
- Unit conversion mismatch in recipe lines.
- Supplier delivery split across multiple receipts.

## 9. Performance Considerations
- Precomputed stock-on-hand cache for dashboard reads.
- Async consumption processing with retry and dead-letter queue.
- Bulk movement insertion for receiving large POs.

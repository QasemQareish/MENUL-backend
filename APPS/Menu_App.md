# Menu Management App

## 1. Overview
**Purpose:** Authoritative domain for menu structure, items, pricing, availability, and publish lifecycle.

**Main responsibilities:**
- Manage categories/items per kitchen and branch.
- Handle price books and scheduled changes.
- Control item availability and metadata.
- Publish menu versions consumed by POS and ordering channels.

## 2. Core Features
- Category hierarchy and kitchen assignment.
- Item CRUD with descriptions, allergens, tags, prep times.
- Branch-specific price overrides.
- Time-window availability (breakfast/lunch/dinner).
- Bulk import/export (CSV/API).
- Draft -> review -> publish workflow with rollback.

## 3. Backend Design
### Services/modules
- `catalog-service` (categories/items)
- `pricing-service` (base prices, overrides, effective price)
- `availability-service` (time and stock state)
- `publish-service` (version snapshots)

### Business logic breakdown
- Effective price resolves in order: branch override -> restaurant base -> default.
- Publish creates immutable snapshot consumed downstream.
- Category/kitchen integrity constraints enforced before publish.

### API endpoints (examples)
- `GET /v1/menu/categories`
- `POST /v1/menu/items`
- `PATCH /v1/menu/items/{id}/availability`
- `POST /v1/menu/pricing/overrides`
- `POST /v1/menu/publish`
- `GET /v1/menu/snapshots/{version}`

## 4. Database Design
### Tables
- `categories(id, tenant_id, branch_id, kitchen_id, name, parent_id, sort_order)`
- `items(id, tenant_id, category_id, kitchen_id, sku, name, description, base_price, is_active)`
- `item_prices(id, tenant_id, item_id, branch_id, price, starts_at, ends_at)`
- `item_availability(id, tenant_id, item_id, branch_id, day_of_week, start_time, end_time, is_available)`
- `menu_snapshots(id, tenant_id, branch_id, version, payload_json, created_by, created_at)`

### Relationships
- category 1..* items.
- item 1..* item_prices / item_availability.

### Indexes
- unique `(tenant_id, branch_id, version)` for snapshots.
- unique `(tenant_id, sku)`.
- index `item_prices(item_id, branch_id, starts_at DESC)`.

### Scaling considerations
- Snapshot payloads in object storage + metadata pointer in DB.
- Redis cache keyed by `tenant:branch:menu_version` for POS startup.

## 5. UI/UX Specification
### Screens
- Categories Manager.
- Items Catalog Editor.
- Pricing & Overrides.
- Availability Calendar.
- Publish Review & Diff.

### Layout/components
- Tree panel (categories) + item detail pane.
- Bulk edit grid for pricing/availability.

### Interactions
- Inline conflict warnings (overlapping availability windows).
- Publish diff shows added/removed/changed items and prices.

## 6. User Roles (per app)
- Owner, Branch Manager, Kitchen Manager (write within scope).
- Chef (read-only visibility for prep context).

## 7. Data Flow
- Edit drafts in catalog tables -> publish snapshot -> emit `menu.published` event.
- POS and Orders subscribe/cache latest published version per branch.

## 8. Edge Cases
- Item mapped to deleted kitchen.
- Price override overlapping existing active range.
- Publish attempted with orphan categories.

## 9. Performance Considerations
- Precompute effective price view/materialization.
- CDN/object storage for static menu media assets.
- Incremental cache invalidation per changed item on publish.

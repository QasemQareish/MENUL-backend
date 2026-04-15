# POS App

## 1. Overview
**Purpose:** High-speed front-of-house user interface for table service and checkout operations.

**Main responsibilities:**
- Table map and occupancy management.
- Rapid order entry and modification.
- Settlement flow (split bills, discounts, payment method capture).
- Receipt and shift-end operations.

## 2. Core Features
- Branch-aware table list/floor map.
- Menu browsing with fast search and favorites.
- Item modifiers/notes and quantity controls.
- Hold/send order flows.
- Split/merge checks and payment summary.
- Offline-safe local queue for transient network failures.

## 3. Backend Design
### Services/modules
- `pos-bff` (backend-for-frontend)
- `table-session-client` (Orders integration)
- `menu-read-client` (Menu snapshot cache)
- `payment-adapter-client`

### Business logic breakdown
- POS does not own order truth; delegates writes to Orders app.
- Local command queue uses idempotency keys to prevent duplicates.
- Branch policy rules (tax/service) loaded from Admin app config.

### API endpoints (examples)
- `GET /v1/pos/bootstrap`
- `GET /v1/pos/tables`
- `POST /v1/pos/commands/add-item`
- `POST /v1/pos/commands/close-session`
- `POST /v1/pos/payments/intents`

## 4. Database Design
### Tables
- `pos_devices(id, tenant_id, branch_id, device_name, status, last_seen_at)`
- `pos_command_log(id, tenant_id, device_id, idempotency_key, command_type, payload_json, result_status, created_at)`
- `shift_summaries(id, tenant_id, branch_id, cashier_user_id, opened_at, closed_at, gross_total, cash_total, card_total)`

### Relationships
- device 1..* command_log.
- shift linked to branch and cashier.

### Indexes
- unique `(tenant_id, idempotency_key)` on command log.
- index `shift_summaries(branch_id, opened_at DESC)`.

### Scaling considerations
- Keep POS DB minimal (operational cache/log only).
- TTL policy for command log records after archival.

## 5. UI/UX Specification
### Screens
- Login/branch selection.
- Floor map & table status.
- Order composer.
- Bill checkout and payment screen.
- Shift close summary.

### Layout/components
- Two-pane order composer (menu left, cart right).
- Sticky action bar for send/hold/pay.

### Interactions
- Keyboard-first shortcuts for speed.
- Immediate visual feedback for sync state (queued/sent/failed).

## 6. User Roles (per app)
- Waiter, Cashier, Branch Manager.

## 7. Data Flow
- POS fetches bootstrap config/menu snapshot.
- User actions create commands -> POS BFF -> Orders API.
- Status updates stream back to UI from Orders events.

## 8. Edge Cases
- Device offline during active shift.
- Table transfer while kitchen still processing prior items.
- Partial payment failure and retry.

## 9. Performance Considerations
- Aggressive local caching for menu and table state.
- Delta updates via WebSocket instead of full polling.
- Background sync worker for queued commands.

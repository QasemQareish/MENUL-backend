# Orders App

## 1. Overview
**Purpose:** Transactional engine for order sessions and item lifecycle, acting as the canonical source for live order state.

**Main responsibilities:**
- Open/reuse/close order sessions per table.
- Create/update/cancel order items with strict state machine.
- Route items to kitchen workflows.
- Maintain totals, payment status hooks, and timeline events.

## 2. Core Features
- Unique active session per table.
- Guest ordering support via session password/token.
- Item status transitions with policy checks.
- Partial cancellation and notes.
- SLA timestamps (accepted_at, ready_at, served_at).
- Order timeline and audit trail.

## 3. Backend Design
### Services/modules
- `session-service`
- `order-item-service`
- `kitchen-routing-service`
- `pricing-snapshot-service`
- `event-publisher`

### Business logic breakdown
- On item creation, price snapshot is copied from Menu effective price.
- Transition guardrails enforce allowed moves by role (e.g., chef cannot set paid).
- Session close rotates table guest secret and locks customer edits.

### API endpoints (examples)
- `POST /v1/orders/sessions`
- `GET /v1/orders/sessions/{id}`
- `POST /v1/orders/items`
- `PATCH /v1/orders/items/{id}/status`
- `POST /v1/orders/sessions/{id}/close`
- `GET /v1/orders/kitchens/{kitchen_id}/queue`

## 4. Database Design
### Tables
- `order_sessions(id, tenant_id, branch_id, table_id, customer_id, active, session_secret_hash, total_amount, payment_status, opened_at, closed_at)`
- `order_items(id, tenant_id, session_id, item_id, kitchen_id, quantity, unit_price_snapshot, notes, status, created_at, updated_at)`
- `order_item_events(id, tenant_id, order_item_id, from_status, to_status, actor_user_id, created_at)`
- `payment_links(id, tenant_id, session_id, provider, external_ref, status, amount)`

### Relationships
- session 1..* order_items.
- order_item 1..* order_item_events.

### Indexes
- partial unique `order_sessions(table_id) WHERE active=true`.
- index `order_items(kitchen_id, status, created_at)` for queue retrieval.
- index `order_sessions(branch_id, active, opened_at DESC)`.

### Scaling considerations
- Shard/partition by `tenant_id` for very large operators.
- Keep event table append-only and archive cold partitions.

## 5. UI/UX Specification
### Screens
- Live Order Board (per branch).
- Session Detail with timeline.
- Kitchen Queue View.
- Table session opener/closer modal.

### Layout/components
- Real-time status chips and elapsed-time badges.
- Inline item note editing with permission gates.

### Interactions
- Optimistic UI with server reconciliation for status updates.
- Color-coded SLA breaches for delayed items.

## 6. User Roles (per app)
- Waiter, Branch Manager, Owner, Admin, Kitchen Manager, Chef, Guest/Customer (limited).

## 7. Data Flow
- POS creates item -> Orders persists + emits `order.item.added`.
- Kitchen app updates status -> Orders validates -> emits `order.item.status_changed`.
- Session close emits settlement and analytics events.

## 8. Edge Cases
- Duplicate item submissions from flaky network (idempotency key required).
- Kitchen status update arrives after session closure.
- Menu item deactivated after being ordered.

## 9. Performance Considerations
- WebSocket/SSE stream for live queues.
- Write-optimized schema; heavy analytics moved to event consumers.
- Batched recalculation of session totals on high-volume edits.

# 08) Database Design

## Storage Strategy
- OLTP: PostgreSQL for transactional consistency.
- Analytics: warehouse/lakehouse sink via CDC/events.

## Core Tables
- `tenants`, `branches`, `users`, `roles`, `permissions`
- `menus`, `menu_items`, `recipes`, `prices`
- `orders`, `order_lines`, `payments`, `refunds`
- `inventory_items`, `inventory_ledger`, `purchase_orders`
- `customers`, `loyalty_accounts`, `campaign_events`
- `audit_logs`, `outbox_events`, `idempotency_keys`

## Key Constraints
- Composite tenant-aware uniques (e.g., `(tenant_id, branch_code)`).
- FK constraints scoped by `tenant_id`.
- Check constraints for monetary non-negativity and valid statuses.

## Indexing
- Hot-path indexes: `(tenant_id, created_at desc)` on orders/payments.
- Search indexes: `(tenant_id, customer_phone/email)`.
- Partial indexes for active/open entities.

## Partitioning
- Range partition by month for high-volume tables (`orders`, `inventory_ledger`, `audit_logs`).
- Optional sub-partition by tenant cohort for very large tenants.

## Consistency Patterns
- Transactional outbox for event publication.
- Idempotency table for write replay protection.
- Optimistic concurrency for offline sync conflict detection.

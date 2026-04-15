# Admin / Control Panel App

## 1. Overview
**Purpose:** Central tenant administration console for organizational setup, policy configuration, and platform governance.

**Main responsibilities:**
- Restaurant/branch/table topology administration.
- Kitchen setup and operational policy management.
- Feature flags and integration credentials.
- Operational audit and support tools.

## 2. Core Features
- Tenant onboarding and branch provisioning workflows.
- Table templates (floor, numbering, seat defaults).
- Kitchen ownership mapping and shift policies.
- Tax/service charge/payment method configuration.
- Global business hours and blackout windows.
- Support actions: account unlock, temporary impersonation with logging.

## 3. Backend Design
### Services/modules
- `tenant-config-service`
- `topology-service`
- `policy-service`
- `support-tools-service`

### Business logic breakdown
- All mutating actions require elevated permission + reason code.
- Configuration changes versioned with rollback checkpoints.
- Write operations emit immutable admin audit events.

### API endpoints (examples)
- `POST /v1/admin/tenants`
- `POST /v1/admin/branches`
- `POST /v1/admin/tables/bulk`
- `PATCH /v1/admin/policies/tax`
- `PATCH /v1/admin/feature-flags/{flag}`
- `POST /v1/admin/support/impersonations`

## 4. Database Design
### Tables
- `tenants(id, name, plan, status, created_at)`
- `restaurants(id, tenant_id, name, owner_user_id, default_language, branding_json)`
- `branches(id, tenant_id, restaurant_id, name, location, timezone, is_active)`
- `tables(id, tenant_id, branch_id, table_number, seats, floor_zone)`
- `kitchens(id, tenant_id, branch_id, name, status)`
- `policies(id, tenant_id, policy_type, policy_json, version, active)`
- `admin_audit_log(id, tenant_id, actor_user_id, action, object_type, object_id, reason, created_at)`

### Relationships
- tenant -> restaurants/branches/policies.
- restaurant -> branches.
- branch -> tables/kitchens.

### Indexes
- unique `(tenant_id, restaurant_id, branch_name)`.
- unique `(tenant_id, branch_id, table_number)`.
- index `admin_audit_log(tenant_id, created_at DESC)`.

### Scaling considerations
- Store policy JSON in versioned rows for deterministic rollback.
- Partition audit log by month for retention and fast queries.

## 5. UI/UX Specification
### Screens
- Tenant Overview.
- Restaurant & Branch Management.
- Table/Floor Plan Manager.
- Kitchen & Routing Setup.
- Policy Configuration Center.
- Feature Flag Console.
- Audit & Support Activity Viewer.

### Layout/components
- Wizard-based creation flows to reduce configuration drift.
- Side-by-side “current vs draft policy” comparison.

### Interactions
- Dry-run validation before applying policy changes.
- Confirmation dialogs requiring typed reason for critical changes.

## 6. User Roles (per app)
- Superadmin, Admin, Owner (limited scope), Branch Manager (local scope).

## 7. Data Flow
- Config updates -> persisted versioned policy -> publish `config.updated` event.
- Downstream apps subscribe and update local caches/read models.

## 8. Edge Cases
- Branch deactivation while active sessions exist.
- Kitchen deletion with mapped menu categories.
- Concurrent policy edits by multiple admins.

## 9. Performance Considerations
- Heavy read caching for topology endpoints used by POS startup.
- Asynchronous propagation of non-critical config updates.
- Optimistic locking (`version`) for policy writes.

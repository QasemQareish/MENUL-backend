# Restaurant OS SaaS — System Decomposition & Integration Blueprint

## 1) System Decomposition

### 1. POS App
**Purpose:** Front-of-house operational console used by waiters and cashiers to manage tables, in-person ordering, and settlement.

**Responsibilities:**
- Table occupancy and session lifecycle (open/close/merge/move).
- Fast item entry (search, favorites, modifiers, notes).
- Bill split, discount application, payment capture handoff.
- Receipt printing and end-of-shift reconciliation input.

**Why separated:**
- Requires ultra-low latency UX and offline/edge tolerance.
- Release cycle differs from back-office apps.
- Hardware integration (printers, POS terminals) should not block core domain releases.

### 2. Orders App
**Purpose:** Canonical order orchestration domain controlling order state transitions and routing to kitchen workflows.

**Responsibilities:**
- Order session creation and lifecycle.
- Order item state machine (`pending -> accepted -> cooking -> ready -> served/cancelled`).
- Concurrency rules, idempotent updates, audit events.
- Ticket routing by kitchen and SLA timestamps.

**Why separated:**
- High write throughput and strict consistency requirements.
- Core business criticality warrants independent scaling and observability.

### 3. Menu Management App
**Purpose:** Source of truth for categories, items, pricing, availability, and kitchen mapping.

**Responsibilities:**
- Multi-branch menu structures.
- Price books and branch overrides.
- Item metadata (allergens, prep time, tags).
- Publish workflow and versioning.

**Why separated:**
- Editorial/back-office workflow differs from runtime ordering flow.
- Menu changes need controlled publishing and rollback independent from ordering runtime.

### 4. Inventory App
**Purpose:** Tracks ingredients, stock movement, depletion, and procurement signals.

**Responsibilities:**
- Ingredient ledger by branch and storage location.
- Recipe/BOM linkage to menu items.
- Auto-decrement on served or accepted kitchen output.
- Waste/adjustment records and low-stock alerts.

**Why separated:**
- Requires ledger-style data model and reconciliation batch jobs.
- Different KPI set and user persona (operations/procurement).

### 5. CRM App
**Purpose:** Customer profile and loyalty context powering personalized service.

**Responsibilities:**
- Customer identity stitching (phone/email/device/session).
- Visit/order history timeline.
- Loyalty points and tier management.
- Consent/preferences management.

**Why separated:**
- PII governance and compliance boundaries.
- Can scale/read optimize separately from transactional order path.

### 6. Marketing App
**Purpose:** Campaign orchestration and promotion rules execution.

**Responsibilities:**
- Promotion rule engine (bundle, % discount, BOGO, time windows).
- Campaign segmentation and targeting.
- Channel delivery orchestration (email/SMS/push integrations).
- Redemption tracking and budget control.

**Why separated:**
- Heavier experimentation cadence and third-party integrations.
- Non-critical runtime should not impact core ordering availability.

### 7. Analytics App
**Purpose:** Decision-support layer for business, ops, and product metrics.

**Responsibilities:**
- ETL/ELT from operational event streams.
- Curated marts (sales, labor, menu performance, SLA).
- Dashboards and scheduled reports.
- Forecasting primitives (demand, stockout risk).

**Why separated:**
- Read-intensive analytical workloads should not query OLTP stores directly.
- Supports polyglot data infra and slower processing windows.

### 8. Admin/Control Panel App
**Purpose:** Tenant administration and global configuration plane.

**Responsibilities:**
- Restaurant/branch/kitchen topology management.
- Operational policy controls (tax, service charge, order rules).
- Feature flags and tenant provisioning.
- Support tooling (impersonation, incident notes, audit browse).

**Why separated:**
- Central governance plane with stricter authorization and audit requirements.
- Changes should be isolated from operational front-line UX.

### 9. Auth & User Management App
**Purpose:** Central identity, authentication, and role-based access control for all apps.

**Responsibilities:**
- Login, token issuance/refresh/revocation.
- User lifecycle, role hierarchy, and scope assignment.
- MFA, password reset, verification workflows.
- Service-to-service auth and policy enforcement hooks.

**Why separated:**
- Security boundary with strict hardening and independent compliance roadmap.
- All other apps depend on stable auth contracts.

---

## 2) Architecture Overview

### Recommended style: **Domain Microservices + Internal Modular Monolith per app**

**Decision:**
- Platform-level = microservice decomposition by domain app.
- Inside each app = modular monolith (clear modules, shared transaction boundary where needed).

**Why this hybrid is optimal:**
- Avoids “distributed monolith” by aligning services to clear domain ownership.
- Keeps implementation complexity manageable per team/app.
- Enables independent deployments while preserving local developer speed.

### Communication model

- **Synchronous REST/gRPC** for command/query needing immediate response.
  - Example: POS requests menu availability snapshot.
- **Asynchronous events** via message bus (Kafka/RabbitMQ/SNS+SQS equivalent) for decoupled propagation.
  - Example: `order_item.ready` triggers CRM timeline + analytics ingestion.
- **Outbox pattern** in each write-service to guarantee event publishing consistency.
- **Idempotency keys** on command endpoints exposed to POS and external integrations.

### Data ownership rules

- Each app owns its database schema and writes only to its own store.
- Cross-app reads happen through:
  1) app-owned APIs,
  2) replicated read models,
  3) event-fed denormalized projections.
- No cross-database foreign keys across services.
- Tenant boundary (`tenant_id`) enforced in every primary table and token claim.

---

## 3) Cross-App Integration

### Shared services
- **Auth service**: OIDC/JWT issuer, RBAC policy claims.
- **Notification service** (internal platform utility): email/SMS/push abstraction with retry DLQ.
- **Audit service**: immutable append-only activity log for admin/security events.
- **Config service**: feature flags, environment controls, per-tenant rollout policy.

### Core event contracts (examples)
- `order.session.opened`
- `order.item.added`
- `order.item.status_changed`
- `order.session.closed`
- `menu.item.updated`
- `inventory.stock.adjusted`
- `crm.customer.merged`
- `marketing.promo.redeemed`

Each event must include:
- `event_id` (UUID), `event_type`, `occurred_at`
- `tenant_id`, `branch_id` (where applicable)
- `schema_version`
- stable payload with additive-only evolution policy

### API contract principles
- Versioned endpoints (`/v1/...`) and explicit deprecation windows.
- Contract tests between producer and consumer services.
- Error model standard (`code`, `message`, `details`, `request_id`).
- Timeout budgets and retry/backoff guidelines documented per dependency.

---

## 4) Development Priority & Delivery Sequence

1. **Auth & User Management App**
   - Foundation for identity, token propagation, and role scopes.
2. **Admin/Control Panel App**
   - Required to provision tenants/branches/kitchens and policies.
3. **Menu Management App**
   - Needed before order entry can be useful.
4. **Orders App**
   - Core transaction engine.
5. **POS App**
   - Operational UI depending on Menu + Orders + Auth.
6. **Inventory App**
   - Integrates with menu recipes and order consumption.
7. **CRM App**
   - Starts collecting longitudinal customer context.
8. **Marketing App**
   - Uses CRM segments and order signals for targeting.
9. **Analytics App**
   - Can begin early with skeleton ingestion, but full value comes after transactional apps stabilize.

### Dependency highlights
- POS depends on Auth, Menu, Orders.
- Inventory depends on Menu and Orders events.
- Marketing depends on CRM identity and Orders outcomes.
- Analytics depends on events from all domains.


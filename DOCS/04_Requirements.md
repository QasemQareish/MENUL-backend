# 04) Requirements

## Functional Requirements

### Core Commerce
- **FR-001** POS shall support dine-in, takeaway, and delivery order modes.
- **FR-002** OMS shall enforce order lifecycle states and SLA timestamps.
- **FR-003** Payment workflow shall support split bills, refunds, and void controls.
- **FR-004** Kitchen routing shall dispatch items by station and prep profile.

### Inventory and Menu
- **FR-005** Inventory shall track stock by SKU, batch, and location.
- **FR-006** Recipe mapping shall deduct ingredient quantities per sold item.
- **FR-007** Menu builder shall support variant pricing, bundles, and time-based availability.
- **FR-008** Menu publishing shall support per-tenant and per-branch overrides.

### CRM and Marketing
- **FR-009** CRM shall maintain customer profiles, preferences, and visit history.
- **FR-010** Campaign engine shall support audience segmentation and multi-channel templates.
- **FR-011** Loyalty shall support points, tiers, and redemption constraints.

### Multi-Tenant and Platform
- **FR-012** Tenant onboarding shall provision isolated data boundaries and defaults.
- **FR-013** Tenant branding shall support themes, logos, localized assets.
- **FR-014** RBAC shall enforce permission scopes by module + branch.
- **FR-015** Public APIs shall be versioned and backward compatible within policy windows.

### Real-Time and Offline
- **FR-016** Kitchen and order boards shall update in near-real-time.
- **FR-017** POS client shall support offline transactions with conflict-safe sync.
- **FR-018** Sync engine shall provide idempotency and replay protection.

### Analytics and AI Readiness
- **FR-019** Event streams shall capture operational and commercial telemetry.
- **FR-020** Reporting shall expose KPI datasets by tenant/time/branch dimensions.
- **FR-021** Feature store contracts shall support future prediction/recommendation models.

## Non-Functional Requirements
- **NFR-001 Availability:** 99.95% monthly availability for core transaction APIs.
- **NFR-002 Latency:** P95 POS write < 250ms in-region.
- **NFR-003 Scalability:** Horizontal scale for stateless services and queue consumers.
- **NFR-004 Security:** Zero cross-tenant data leakage tolerance.
- **NFR-005 Compliance:** Regional tax/privacy controls and auditable logs.
- **NFR-006 Durability:** Transaction and event durability with point-in-time recovery.
- **NFR-007 Observability:** Full tracing for critical transaction journeys.

## Constraints
- Existing codebase is Django modular monolith.
- Current default DB (SQLite) is non-production; PostgreSQL required.
- Migration path must preserve current tenant data and API compatibility.

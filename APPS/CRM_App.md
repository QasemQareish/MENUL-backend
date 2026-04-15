# CRM App

## 1. Overview
**Purpose:** Customer identity and relationship intelligence layer for service personalization and retention.

**Main responsibilities:**
- Customer profile management and identity resolution.
- Visit/order timeline aggregation.
- Loyalty points/tier management.
- Consent and communication preference tracking.

## 2. Core Features
- Customer lookup by phone/email/loyalty ID.
- Duplicate profile merge workflow.
- Loyalty accrual and redemption ledger.
- Visit frequency and RFM segmentation fields.
- Preference tags (dietary, seating, contact channel).

## 3. Backend Design
### Services/modules
- `profile-service`
- `identity-resolution-service`
- `loyalty-service`
- `consent-service`

### Business logic breakdown
- Identity graph links multiple identifiers to one canonical profile.
- Loyalty points rules versioned and evaluated on order settlement.
- Consent checks enforced before campaign targeting exports.

### API endpoints (examples)
- `POST /v1/crm/customers`
- `GET /v1/crm/customers/{id}`
- `POST /v1/crm/customers/merge`
- `POST /v1/crm/loyalty/accrual`
- `PATCH /v1/crm/customers/{id}/preferences`

## 4. Database Design
### Tables
- `customers(id, tenant_id, first_name, last_name, phone, email, birth_date, created_at)`
- `customer_identities(id, tenant_id, customer_id, identity_type, identity_value_hash, verified)`
- `customer_visits(id, tenant_id, customer_id, branch_id, order_session_id, total_spend, visited_at)`
- `loyalty_accounts(id, tenant_id, customer_id, points_balance, tier_code)`
- `loyalty_ledger(id, tenant_id, loyalty_account_id, points_delta, reason, ref_type, ref_id, created_at)`
- `customer_consents(id, tenant_id, customer_id, channel, status, updated_at)`

### Relationships
- customer 1..* identities/visits/consents.
- customer 1..1 loyalty_account.

### Indexes
- unique `(tenant_id, phone)` nullable-safe.
- index `customer_visits(customer_id, visited_at DESC)`.
- index `loyalty_ledger(loyalty_account_id, created_at DESC)`.

### Scaling considerations
- Hash sensitive identifiers for privacy-preserving lookups.
- Stream visit events asynchronously to avoid blocking order close.

## 5. UI/UX Specification
### Screens
- Customer Search.
- Customer 360 Profile.
- Loyalty Dashboard.
- Merge & Conflict Resolution.
- Consent Management.

### Layout/components
- Timeline view combining visits, notes, and loyalty events.
- Identity confidence indicators in merge flow.

### Interactions
- One-click “apply known preferences” in service context.
- Merge confirmation requires selecting canonical source for each field.

## 6. User Roles (per app)
- Waiter (read basic profile), Branch Manager, Owner, Marketing Manager.

## 7. Data Flow
- Orders session close event -> CRM records visit and spend.
- CRM emits `crm.segment.updated` for Marketing audiences.

## 8. Edge Cases
- Same phone shared by family members.
- Retroactive order attribution to customer after guest flow.
- Consent revoked mid-campaign execution.

## 9. Performance Considerations
- Search index (trigram/full-text) for quick customer retrieval.
- Cache top-visited customer summaries by branch.
- Batch loyalty recomputations for corrected historical orders.

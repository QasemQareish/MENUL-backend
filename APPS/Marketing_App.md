# Marketing App

## 1. Overview
**Purpose:** Campaign execution and promotion orchestration service that drives demand and repeat purchases.

**Main responsibilities:**
- Campaign planning and scheduling.
- Promotion rule definition and eligibility checks.
- Audience targeting using CRM segments.
- Redemption tracking and ROI analytics feed.

## 2. Core Features
- Multi-channel campaigns (email/SMS/push).
- Coupon and promo code generation.
- Time/branch/channel restrictions.
- A/B test support for offer variants.
- Budget limits and auto-pause thresholds.

## 3. Backend Design
### Services/modules
- `campaign-service`
- `promotion-engine`
- `audience-service`
- `delivery-orchestration-service`

### Business logic breakdown
- Eligibility evaluated at order composition/checkout time.
- Promotion stacking rules prevent invalid combination abuse.
- Redemption events reconciled with campaign budget.

### API endpoints (examples)
- `POST /v1/marketing/campaigns`
- `POST /v1/marketing/promotions`
- `POST /v1/marketing/audiences/preview`
- `POST /v1/marketing/promotions/evaluate`
- `GET /v1/marketing/campaigns/{id}/performance`

## 4. Database Design
### Tables
- `campaigns(id, tenant_id, name, status, start_at, end_at, channel_config_json, budget_amount)`
- `promotions(id, tenant_id, code, type, rule_json, stacking_group, active)`
- `campaign_audiences(id, tenant_id, campaign_id, segment_query_json, estimated_size)`
- `redemptions(id, tenant_id, promotion_id, order_session_id, customer_id, discount_amount, redeemed_at)`
- `delivery_jobs(id, tenant_id, campaign_id, channel, payload_json, status, attempts, scheduled_at)`

### Relationships
- campaign 1..* delivery_jobs.
- promotion 1..* redemptions.

### Indexes
- unique `(tenant_id, code)` for promotions.
- index `redemptions(promotion_id, redeemed_at DESC)`.
- index `delivery_jobs(status, scheduled_at)` for worker pull.

### Scaling considerations
- Queue-backed campaign delivery workers with concurrency controls.
- Store large audience snapshots in object storage and reference by pointer.

## 5. UI/UX Specification
### Screens
- Campaign Planner.
- Promotion Rules Builder.
- Audience Segment Preview.
- Delivery Monitor.
- Redemption & ROI Dashboard.

### Layout/components
- Visual rule builder for promotion conditions.
- Timeline scheduler with blackout period overlays.

### Interactions
- “What customer sees” simulation for promo rules.
- Live estimate updates as audience filters change.

## 6. User Roles (per app)
- Marketing Manager, Owner, Admin (approval), Analyst (read).

## 7. Data Flow
- CRM provides target segment snapshots.
- Orders calls promotion evaluate API during checkout.
- Redemption events feed Analytics and campaign budget monitors.

## 8. Edge Cases
- Promo code leak causes rapid over-redemption.
- Campaign overlap creates ambiguous discount precedence.
- Delivery provider outage for one channel.

## 9. Performance Considerations
- Precompile promotion rules for low-latency checkout evaluation.
- Use rate-limited worker pools per channel provider.
- Cache active promo set per branch/time window.

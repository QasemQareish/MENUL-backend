# 09) Multi-Tenant Architecture

## Isolation Options

## Option A: Database per Tenant
- **Pros:** strongest isolation, easier data residency/compliance boundaries, blast-radius reduction.
- **Cons:** operational overhead, higher cost at scale, schema management complexity.
- **Best for:** enterprise tenants with strict compliance and high ARPU.

## Option B: Shared Database, Shared Schema (with tenant_id)
- **Pros:** cost efficient, simpler operations, fast onboarding.
- **Cons:** higher leakage risk if controls fail; noisy-neighbor risk.
- **Best for:** SMB tenants and long-tail onboarding.

## Recommended Hybrid Strategy
- Default to shared schema with strict row-level controls.
- Promote strategic tenants to dedicated DB tier based on compliance/traffic SLA.

## Data Partitioning
- Mandatory `tenant_id` on all business tables.
- Row-level security (RLS) policies in PostgreSQL.
- Tenant-aware query middleware and policy enforcement at service layer.

## Tenant Onboarding Flow
1. Create tenant record and subscription plan.
2. Provision tenant config (locale, currency, timezone, tax profile).
3. Seed roles/permissions and default workflows.
4. Provision branding assets and theme tokens.
5. Initialize branch/terminal setup.
6. Run validation checklist and activate tenant.

## Customization System
- Theme tokens: colors, typography, spacing.
- Brand assets: logos, receipt templates, customer app skin.
- Workflow toggles: feature flags by plan/region/tenant.

## Data Isolation Controls
- Tenant-scoped JWT claims.
- RLS + service-level authorization checks.
- Encryption keys separated by tenant tier (envelope encryption strategy).

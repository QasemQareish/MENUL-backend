# 13) Role and Permissions

## Core Roles
- **Owner:** full tenant governance, billing, policy, cross-branch analytics.
- **Manager:** branch-level operations, staffing, inventory approvals, local campaigns.
- **Cashier:** POS checkout, refunds within configured thresholds, customer enrollment.
- **Kitchen Staff:** ticket handling, prep status updates, substitution/cancel requests.
- **Customer:** profile, orders, loyalty redemption, consent preferences.

## RBAC Model
- Permission tuple: `(module, action, scope)`.
- Scope hierarchy: tenant > branch > terminal > own-record.
- Deny-by-default; explicit grants only.

## Policy Examples
- Cashier cannot publish global menu changes.
- Kitchen staff cannot access payment data.
- Manager can approve inventory adjustments for assigned branch only.
- Owner can view cross-branch P&L and campaign performance.

## Governance
- Permission changes require audit trail with actor + reason.
- Time-bound elevated access for incident response.

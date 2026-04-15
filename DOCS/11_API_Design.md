# 11) API Design

## API Paradigm
- Primary: REST (resource-oriented, versioned `/v1`).
- Secondary: GraphQL read gateway (future) for analytics-heavy UI composition.

## Endpoint Structure (Examples)
- `POST /v1/auth/login`
- `POST /v1/tenants/{tenantId}/orders`
- `PATCH /v1/tenants/{tenantId}/orders/{orderId}/status`
- `GET /v1/tenants/{tenantId}/inventory/items?branchId=...`
- `POST /v1/tenants/{tenantId}/campaigns`

## AuthN/AuthZ
- JWT access tokens with tenant + role claims.
- OAuth2/OIDC federation for enterprise SSO.
- Fine-grained authorization by role + branch scope + module permission.

## API Reliability Controls
- Idempotency-Key header for payment/order create endpoints.
- Pagination, filtering, sorting standards.
- Versioning policy with deprecation windows.

## Rate Limiting
- Per-tenant + per-client token buckets.
- Burst and sustained limits by subscription tier.
- Elevated protection for auth/payment endpoints.

## Error Contract
- Standard envelope: `code`, `message`, `details`, `trace_id`.
- Deterministic error taxonomy for client-side handling.

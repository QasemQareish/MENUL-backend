# Auth & User Management App

## 1. Overview
**Purpose:** Centralized identity provider and authorization control plane for all Restaurant OS applications.

**Main responsibilities:**
- Authentication (password, optional OTP/MFA, token refresh/revoke).
- User lifecycle (create, activate, suspend, reset credentials).
- RBAC + scope mapping (tenant/restaurant/branch/kitchen).
- Session/device tracking and security audit.

## 2. Core Features
- Email/username login with JWT access+refresh.
- Refresh token rotation and blacklist/revocation.
- Password reset + email verification flow.
- Optional step-up authentication for sensitive actions.
- Role hierarchy enforcement (superadmin -> admin -> owner -> manager roles -> operator roles).
- Service account credentials for inter-service auth.

## 3. Backend Design
### Services/modules
- `identity-service`: registration/login/password flows.
- `token-service`: issuance, refresh, revocation, JWK rotation.
- `rbac-service`: role + scope grant management.
- `security-service`: risk checks, rate limits, lockouts.

### Business logic breakdown
- Token claims include `tenant_id`, `role`, and scope IDs.
- Role assignment validates hierarchy and ownership chain.
- Privileged route access uses policy engine + scope checks.

### API endpoints (examples)
- `POST /v1/auth/login`
- `POST /v1/auth/refresh`
- `POST /v1/auth/logout`
- `POST /v1/auth/password/reset/request`
- `POST /v1/auth/password/reset/confirm`
- `GET /v1/users/me`
- `POST /v1/users`
- `PATCH /v1/users/{id}/role`

## 4. Database Design
### Tables
- `users(id, tenant_id, email, username, password_hash, status, last_login_at, created_at)`
- `roles(id, code, rank)`
- `user_roles(id, user_id, role_id, tenant_id, restaurant_id, branch_id, kitchen_id)`
- `refresh_tokens(id, user_id, jti, expires_at, revoked_at, device_id)`
- `auth_events(id, user_id, event_type, ip, user_agent, created_at)`

### Relationships
- user 1..* user_roles; role 1..* user_roles.
- user 1..* refresh_tokens.

### Indexes
- unique `(tenant_id, email)` and `(tenant_id, username)`.
- index `refresh_tokens(jti, revoked_at)`.
- composite `user_roles(tenant_id, role_id, branch_id)`.

### Scaling considerations
- Separate token store (Redis) for hot revocation checks.
- Async write auth_events to append-only warehouse sink.

## 5. UI/UX Specification
### Screens
- Login / MFA challenge.
- Profile & active sessions.
- User directory (filter by role/scope).
- Create/edit user wizard.
- Role and permission assignment matrix.

### Layout/components
- Left nav: Users, Roles, Security, Audit.
- Data table with scope chips.
- Inline privilege warnings before save.

### Interactions
- Real-time validation for duplicate username/email.
- “Effective permissions preview” before role assignment.

## 6. User Roles (per app)
- Superadmin, Admin, Owner, Branch Manager, Kitchen Manager.
- Regular operator roles (chef/waiter) primarily consume profile/session screens.

## 7. Data Flow
- Login request -> credential validation -> token issue -> audit event publish.
- Role update -> policy recompute -> downstream cache invalidation event.
- Other apps validate JWT locally and call auth introspection for high-risk operations.

## 8. Edge Cases
- Concurrent token refresh replay attempts.
- User deleted while refresh token still valid.
- Branch reassignment invalidating active app sessions.

## 9. Performance Considerations
- Cache role policy snapshots by `user_id+tenant_id`.
- Use short-lived access token + rotating refresh token.
- Rate limit login and reset endpoints with adaptive penalties.

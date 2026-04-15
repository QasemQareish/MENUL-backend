# 16) Security Design

## Data Isolation
- Tenant claim enforcement on every request.
- Row-level security and tenant-aware DB policies.
- Separate key domains for sensitive tenant tiers.

## Encryption
- TLS 1.2+ in transit.
- AES-256 at rest for databases/backups.
- KMS-backed envelope encryption for secrets and critical payloads.

## Secure Payments
- PCI-aligned tokenization with external payment processors.
- No raw PAN storage in platform services.
- Signed webhook validation and replay protection.

## Threat Protection
- OWASP-aligned controls (SQLi, XSS, CSRF, SSRF).
- WAF, bot mitigation, and adaptive rate limits.
- MFA for privileged users and just-in-time elevated access.

## Audit and Incident Response
- Immutable audit logs for auth, financial, and permission events.
- Security alerting with severity-based runbooks.
- Regular penetration tests and dependency vulnerability scanning.

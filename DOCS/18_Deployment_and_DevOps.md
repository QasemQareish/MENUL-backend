# 18) Deployment and DevOps

## Environments
- Dev, QA, Staging, Production (multi-region where required).

## CI/CD Blueprint
1. Build and test
2. Security and compliance checks
3. Artifact signing
4. Progressive deployment (canary/blue-green)
5. Post-deploy verification

## Infrastructure as Code
- Declarative environment provisioning.
- Drift detection and policy-as-code enforcement.

## Observability Stack
- Centralized logs, distributed tracing, RED/USE metrics.
- SLO dashboards with alerting and on-call rotations.

## Reliability Operations
- Automated backups + restore drills.
- Runbooks for payment outage, sync backlog, DB failover.
- Disaster recovery objectives (RPO/RTO) per plan tier.

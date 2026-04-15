# 15) Performance and Scaling

## Caching Strategy
- L1 in-process cache for config/feature flags.
- L2 distributed cache (Redis) for menu snapshots and session state.
- Cache invalidation via event topics on menu/price updates.

## Load Balancing
- Global traffic manager with geo-routing.
- Regional L7 load balancers with health-based failover.

## Database Scaling
- PostgreSQL primary + read replicas.
- Connection pooling and query budget enforcement.
- Partition high-volume transactional tables.

## Async Processing
- Message queue for non-blocking tasks: receipts, notifications, analytics export.
- Retry with dead-letter queues and poison-message handling.

## SLO and Capacity
- Predefined SLOs per critical API.
- Capacity planning by meal-peak concurrency profiles.
- Regular chaos/load tests for resilience validation.

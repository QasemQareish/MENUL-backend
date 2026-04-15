# 10) System Architecture

## Architectural Style
- Modular monolith core with event-driven extensions.
- API Gateway + identity service + domain services.
- Message bus for async workflows and integrations.

## Logical Layers
1. Experience layer (POS, staff UI, customer UI, admin).
2. API and orchestration layer.
3. Domain services layer (orders, menu, inventory, CRM, marketing).
4. Data layer (OLTP, cache, event log, analytics sink).

## Real-Time Architecture
- WebSocket/SSE channels for kitchen board and order updates.
- Event consumers update read models for low-latency query endpoints.

## Offline-First POS
- Local edge datastore for transaction queue.
- Sync engine with idempotency keys and conflict resolution policies.

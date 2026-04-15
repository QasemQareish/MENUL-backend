# 07) System Models

## Context Model
External actors (customers, staff, owners, payment providers, delivery channels) interact with the Restaurant OS through API gateway and tenant-aware services.

## Domain Model (High Level)
- Tenant -> Branch -> Terminal
- Menu -> Category -> Item -> Recipe
- Order -> OrderLine -> Payment -> Receipt
- StockItem -> InventoryLedger -> PurchaseOrder
- Customer -> LoyaltyAccount -> CampaignInteraction

## Event Model
Key events:
- `order.created`, `order.prepared`, `order.closed`
- `payment.authorized`, `payment.failed`, `payment.refunded`
- `inventory.decremented`, `inventory.low_stock`
- `campaign.sent`, `campaign.converted`

## State Models
- Order: `created -> accepted -> preparing -> ready -> served/fulfilled -> closed`
- Payment: `initiated -> authorized -> captured -> settled` (+ `failed/refunded`)
- Sync: `queued -> transmitted -> acknowledged` (+ `conflict`)

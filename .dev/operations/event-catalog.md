# Event Catalog

## Scope

This catalog tracks the integration events and request/reply contracts that are currently visible in `src/BC-Contracts/` and actively referenced in application/runtime code.

## Event Index

| Name | Type | Producer BC | Consumer BCs | Trigger Use Case | Contract Location | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `ReserveInventoryRequestContract` | request contract | `Orders` caller | `Inventory` handler | `PlaceOrder` | `src/BC-Contracts/Lab.BoundedContextContracts.Inventory/Interactions/ReserveInventoryRequestContract.cs` | active |
| `ReserveInventoryResponseContract` | response contract | `Inventory` handler | `Orders` caller | `PlaceOrder` | `src/BC-Contracts/Lab.BoundedContextContracts.Inventory/Interactions/ReserveInventoryResponseContract.cs` | active |
| `OrderPlaced` | integration event | `Orders` | `Product Consumer`, `Inventory Consumer`, other downstream listeners | `PlaceOrder` | `src/BC-Contracts/Lab.BoundedContextContracts.Orders/IntegrationEvents/OrderPlaced.cs` | active |
| `OrderShipped` | integration event | `Orders` | downstream listeners on `orders.integration.events` | `ShipOrder` | `src/BC-Contracts/Lab.BoundedContextContracts.Orders/IntegrationEvents/OrderShipped.cs` | active |
| `OrderDelivered` | integration event | `Orders` | downstream listeners on `orders.integration.events` | `DeliverOrder` | `src/BC-Contracts/Lab.BoundedContextContracts.Orders/IntegrationEvents/OrderDelivered.cs` | active |
| `OrderCancelled` | integration event | `Orders` | downstream listeners on `orders.integration.events` | `CancelOrder` | `src/BC-Contracts/Lab.BoundedContextContracts.Orders/IntegrationEvents/OrderCancelled.cs` | active |
| `ProductStockDecreasedIntegrationEvent` | integration event | `Inventory` | downstream listeners on `inventory.integration.events` | `DecreaseStock` | `src/BC-Contracts/Lab.BoundedContextContracts.Inventory/IntegrationEvents/ProductStockDecreasedIntegrationEvent.cs` | active |
| `ProductStockIncreasedIntegrationEvent` | integration event | `Inventory` | downstream listeners on `inventory.integration.events` | `IncreaseStock` | `src/BC-Contracts/Lab.BoundedContextContracts.Inventory/IntegrationEvents/ProductStockIncreasedIntegrationEvent.cs` | active |
| `ProductStockReturnedIntegrationEvent` | integration event | `Inventory` | downstream listeners on `inventory.integration.events` | `Restock` | `src/BC-Contracts/Lab.BoundedContextContracts.Inventory/IntegrationEvents/ProductStockReturnedIntegrationEvent.cs` | active |
| `ProductStockDeducted` | integration event | unclear / legacy products contract | not clearly mapped in active code | unclear | `src/BC-Contracts/Lab.BoundedContextContracts.Products/IntegrationEvents.cs` | deferred-review |
| `ProductStockDeductionFailed` | integration event | unclear / legacy products contract | not clearly mapped in active code | unclear | `src/BC-Contracts/Lab.BoundedContextContracts.Products/IntegrationEvents.cs` | deferred-review |

## Event Details

### ReserveInventoryRequestContract

- Business meaning:
  - `Orders` asks `Inventory` to reserve or deduct stock before an order is confirmed.
- Payload summary:
  - `ProductId`
  - `Quantity`
- Producer responsibility:
  - send only for a valid order-placement attempt
- Consumer expectations:
  - `Inventory` handles it by invoking `DecreaseStockCommand`
- Idempotency expectation:
  - not yet explicitly documented; should be treated as duplicate-sensitive
- Ordering expectation:
  - per-product duplicate or re-ordered requests may produce incorrect stock changes if not handled upstream
- Failure handling notes:
  - failure returns `ReserveInventoryResponseContract.Result = false`, which blocks order placement

### ReserveInventoryResponseContract

- Business meaning:
  - reports whether stock reservation succeeded
- Payload summary:
  - `Result`
- Producer responsibility:
  - return success only after inventory command succeeds
- Consumer expectations:
  - `Orders` must not persist or publish `OrderPlaced` when result is false
- Idempotency expectation:
  - caller should not assume retries are harmless without correlation rules
- Ordering expectation:
  - tied to request/reply flow, not standalone event ordering
- Failure handling notes:
  - missing or delayed replies can block order placement flow

### OrderPlaced

- Business meaning:
  - a new order has been accepted and persisted
- Payload summary:
  - `OrderId`, `ProductId`, `ProductName`, `Quantity`, `OccurredOn`
- Producer responsibility:
  - publish after successful persistence and inventory reservation
- Consumer expectations:
  - downstream contexts may update projections or start dependent workflows
- Idempotency expectation:
  - consumers should treat duplicates as possible
- Ordering expectation:
  - should logically precede `OrderShipped`, `OrderDelivered`, and `OrderCancelled`
- Failure handling notes:
  - failed publication risks stale downstream views

### OrderShipped / OrderDelivered / OrderCancelled

- Business meaning:
  - order lifecycle moved to shipped, delivered, or cancelled
- Payload summary:
  - `OrderId`, `OccurredOn`
- Producer responsibility:
  - publish after state transition is persisted
- Consumer expectations:
  - consumers should update order status projections or trigger follow-up actions
- Idempotency expectation:
  - duplicate delivery should be tolerated by consumers
- Ordering expectation:
  - these events should reflect legal lifecycle progression, though exact guard rules still need stronger documentation
- Failure handling notes:
  - out-of-order downstream handling can create inconsistent read models

### ProductStockDecreasedIntegrationEvent

- Business meaning:
  - stock was reduced successfully for a product
- Payload summary:
  - `InventoryItemId`, `ProductId`, `DecreasedQuantity`, `CurrentStock`, `OccurredOn`
- Producer responsibility:
  - publish only after successful stock decrease and persistence
- Consumer expectations:
  - use as a stock-change fact, not as a command
- Idempotency expectation:
  - duplicates should not cause double-reaction downstream
- Ordering expectation:
  - should reflect the actual post-write stock sequence for a product when possible
- Failure handling notes:
  - downstream consumers must not infer this event when the stock decrease failed

### ProductStockIncreasedIntegrationEvent / ProductStockReturnedIntegrationEvent

- Business meaning:
  - stock increased due to supply or return flow
- Payload summary:
  - `InventoryItemId`, `ProductId`, quantity field currently named `DecreasedQuantity`, `CurrentStock`, `OccurredOn`
- Producer responsibility:
  - publish only after persistence
- Consumer expectations:
  - consumers should interpret these as stock-up facts, despite the current quantity property naming
- Idempotency expectation:
  - duplicate handling should be assumed necessary
- Ordering expectation:
  - consumers should not assume these can never interleave with decrease events
- Failure handling notes:
  - property naming inconsistency is a documentation and contract risk that should be tracked

## Delivery Semantics

- Request/reply reservation flow is synchronous from the caller perspective, but still mediated by the message bus.
- Integration events are published through Wolverine with durable outbox enabled in runtime configuration.
- Consumer handling should assume at-least-once delivery unless stronger guarantees are explicitly documented later.

## Ownership and Versioning Rules

- Contract source of truth lives under `src/BC-Contracts/`.
- Producing bounded context owns event meaning and payload compatibility.
- Consumer-specific assumptions should not redefine the producer contract.
- The inventory stock increase/return event quantity property naming inconsistency should be treated as a contract risk, not normalized silently in consumers.

## Deferred Items

- Exact consumer ownership for `products.integration.events` is not fully documented.
- Legacy or unclear product stock deduction contracts need later review to decide whether they are active, deprecated, or obsolete.
- Correlation IDs, versioning policy, and replay rules still need explicit runtime documentation.

# Event Catalog

## Scope

This catalog tracks integration events and request/reply contracts visible in `src/BC-Contracts/`. An `active` status requires a confirmed current producer or request/reply use; configured channels without a confirmed producer are described separately.

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
  - `OperationId`
  - `ProductId`
  - `Quantity`
- Producer responsibility:
  - send only for a valid order-placement attempt
- Consumer expectations:
  - `Inventory` maps it through `ReserveInventoryRequestContractHandler` to `IReserveInventoryUseCase.ExecuteAsync` with `ReserveInventoryInput`
- Idempotency expectation:
  - `OperationId` is the durable identity; same-payload replay returns the stored outcome and mismatched payload returns `OperationIdentityConflict`
- Ordering expectation:
  - per-product duplicate or re-ordered requests may produce incorrect stock changes if not handled upstream
- Failure handling notes:
  - failure returns `ReserveInventoryResponseContract.Result = false`, which blocks order placement

### ReserveInventoryResponseContract

- Business meaning:
  - reports whether stock reservation succeeded
- Payload summary:
  - `OperationId`
  - `Result`
  - `FailureReason`
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
  - increase: `InventoryItemId`, `ProductId`, `IncreasedQuantity`, `CurrentStock`, `OccurredOn`
  - return: `InventoryItemId`, `ProductId`, `ReturnedQuantity`, `CurrentStock`, `OccurredOn`
- Producer responsibility:
  - publish only after persistence
- Consumer expectations:
  - consumers must bind the producer-owned corrected quantity name for each event type
- Idempotency expectation:
  - duplicate handling should be assumed necessary
- Ordering expectation:
  - consumers should not assume these can never interleave with decrease events
- Failure handling notes:
  - the prior erroneous `DecreasedQuantity` fields were removed by owner-approved breaking correction on 2026-08-27; no compatibility alias is retained

## Delivery Semantics

- Request/reply reservation flow is synchronous from the caller perspective, but still mediated by the message bus.
- Orders lifecycle events are atomically staged in `OrderIntegrationOutbox` and relayed with a stable message identity through the PostgreSQL-persisted Orders Wolverine runtime.
- All Inventory commands that emit integration events atomically stage them in `InventoryIntegrationOutbox`. Reservation reuses `OperationId`; decrease/increase/restock generate UUID v7 message IDs. All use normalized `ProductId` as Kafka partition key.
- Inventory relay failure never rolls back already committed stock state. It retries with bounded backoff, parks after five attempts, and sets `PublishedAt` after success. Published rows default to unlimited retention at `Messaging:OutboxRelay:Retention:Mode=RetainAll`.
- Other hosts currently configure durable endpoint flags, but persisted durability is not proven until each host configures and tests a message store.
- Consumer handling should assume at-least-once delivery and deduplicate by stable message identity unless stronger guarantees are explicitly documented later.

## Concrete Consumer-Ownership Examples

These examples separate executable repository behavior from business reactions that are only candidates:

| Status | Message / flow | Producer-owned fact or contract | Consumer-owned reaction | Why ownership matters |
| --- | --- | --- | --- | --- |
| implemented | `ReserveInventoryRequestContract` request/reply | Inventory Published Language owns operation identity, product, quantity, result, and failure meanings | Orders owns when to request reservation and the rule that a failed result blocks order commit; Inventory owns handler mapping, idempotent reservation, and retry policy | The caller cannot redefine `InventoryIsNotEnough`; Inventory cannot decide whether Orders abandons or retries order placement. This is request/reply, not broadcast. |
| configured but handler gap | `OrderPlaced` to `SaleProducts.Consumer` | Orders owns the fact that an order was placed and its schema | Products could own a sales/popularity projection keyed by ProductId and message identity | Changing projection fields or retry policy does not change `OrderPlaced`; changing the event schema requires an Orders compatibility decision. No such handler exists yet, so this is not current behavior. |
| configured but contract gap | `OrderCancelled` to `InventoryControl.Consumer` | Orders owns cancellation fact and reason | Inventory could own compensation/restock, deduplication, and terminal failure handling | The current event lacks ProductId, quantity, or reservation correlation, so safe automatic restock cannot be reconstructed from it alone. The consumer must not guess; either a query/correlation design or producer-approved additive contract is required. |
| external candidate | `ProductStockDecreasedIntegrationEvent` | Inventory owns the stock-change fact, quantity field, current stock, occurrence time, and ProductId ordering key | Search, availability, analytics, or notification consumers each own their own projection/reaction and idempotency | Independent consumers justify separate Kafka consumer groups or RabbitMQ queues. They do not justify changing the Inventory event to match one consumer's internal model. |

Current `SaleProducts.Consumer` and `InventoryControl.Consumer` subscribe to `orders.integration.events`, and `SaleOrders.Consumer` subscribes to `products.integration.events`, but those Consumer projects contain no executable message handlers. Treat the subscription host/topology as compatibility evidence and the business reaction as a gap.

## Ownership and Versioning Rules

- Contract source of truth lives under `src/BC-Contracts/`.
- Producing bounded context owns event meaning and payload compatibility.
- Consumer-specific assumptions should not redefine the producer contract; consumers own reactions, idempotency, retry, and dead-letter handling.
- `ProductStockIncreasedIntegrationEvent.IncreasedQuantity` and `ProductStockReturnedIntegrationEvent.ReturnedQuantity` are the only normative quantity names after the 2026-08-27 owner decision.

## Deferred Items

- `products.integration.events` is configured and has a listener, but current Product use cases do not confirm publication of a product integration event.
- Legacy or unclear product stock deduction contracts need later review to decide whether they are active, deprecated, or obsolete.
- Contract versioning and consumer replay procedures still need explicit runtime documentation; reservation correlation/replay is defined by `OperationId`.
- Kafka + RabbitMQ dual broadcast is a target direction only. It requires destination-aware outbox completion and broker-specific fanout routing before this catalog may call it active.

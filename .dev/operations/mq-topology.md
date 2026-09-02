# MQ Topology

## Scope

This document records the selected topology and the message-bus behavior explicitly visible in current Wolverine configuration. Kafka is canonical. RabbitMQ is retained as a compatibility profile, and Kafka + RabbitMQ dual broadcast is the owner-selected target direction but is not yet implemented.

It distinguishes between:

- known, code-backed Kafka topic names
- known, code-backed RabbitMQ shared queue names that are not a broadcast contract
- unresolved routing behavior that still depends on Wolverine conventions or future runtime review

## Broker Inventory

| Broker Type | Logical Channel | Producer | Consumer | Purpose |
| --- | --- | --- | --- | --- |
| Kafka | `orders.integration.events` | `SaleOrders.WebApi` | `SaleProducts.Consumer`, `InventoryControl.Consumer`, other listeners | order lifecycle integration stream |
| Kafka | `inventory.requests` | `SaleOrders.WebApi` | `InventoryControl.WebApi` | request/reply inventory reservation |
| Kafka | `orders.outbound.replies` | Wolverine reply channel used by `Orders` | `SaleOrders.WebApi` | reply inbox for reservation flow |
| Kafka | `inventory.integration.events` | `InventoryControl.WebApi` | downstream listeners | stock change integration stream |
| Kafka | `products.integration.events` | configured by `SaleProducts.WebApi`; no confirmed current producer use case | `SaleOrders.Consumer` and possible downstream listeners | configured route, not a confirmed active product integration stream |
| RabbitMQ (deferred) | `orders.integration.events` | `SaleOrders.WebApi` | shared queue consumers | Current name implies competing consumers; fanout requires exchange plus one queue per independent subscriber |
| RabbitMQ | `inventory.requests` | `SaleOrders.WebApi` | `InventoryControl.WebApi` | request/reply inventory reservation |
| RabbitMQ | `orders.outbound.replies` | Wolverine reply channel used by `Orders` | `SaleOrders.WebApi` | reply inbox for reservation flow |
| RabbitMQ (deferred) | `inventory.integration.events` | `InventoryControl.WebApi` | shared queue consumers | Current name implies competing consumers, not broadcast |
| RabbitMQ | `products.integration.events` | configured by `SaleProducts.WebApi`; no confirmed current producer use case | `SaleOrders.Consumer` and possible downstream listeners | configured route, not a confirmed active product integration stream |

## Route Map

| Source Message | Source Context | Broker Object | Destination | Behavior Summary |
| --- | --- | --- | --- | --- |
| `OrderPlaced`, `OrderShipped`, `OrderDelivered`, `OrderCancelled` | `Orders` | `orders.integration.events` | product/inventory consumers and other listeners | durable outbox on publish; consumer inbox on listeners |
| `ReserveInventoryRequestContract` | `Orders` | `inventory.requests` | `Inventory` request contract handler | request/reply flow through Wolverine `InvokeAsync` |
| `ReserveInventoryResponseContract` | `Inventory` | `orders.outbound.replies` or Wolverine reply path | `Orders` caller | used as reply path for reservation result |
| `ProductStockDecreasedIntegrationEvent` from `ReserveInventory` or `DecreaseStock` | `Inventory` | `inventory.integration.events` | downstream listeners | producer-created event is atomically staged in `InventoryIntegrationOutbox`, then relayed |
| `ProductStockIncreasedIntegrationEvent`, `ProductStockReturnedIntegrationEvent` | `Inventory` | `inventory.integration.events` | downstream listeners | state and producer-created event are atomically staged through `IInventoryStockOutbox`, then relayed |
| future product integration events implementing `IIntegrationEvent` | `Products` | `products.integration.events` | downstream listeners | route is configured with durable outbox, but no current Product use case confirms publication |

## Retry / Dead-Letter Strategy

Known from current code:

- Kafka listeners use durable inbox where configured.
- RabbitMQ listeners use durable inbox where configured.
- publish routes use durable outbox for integration streams and request messages.
- `SaleOrders.WebApi` configures Wolverine PostgreSQL message persistence in the Orders database.
- `InventoryControl.WebApi` configures Wolverine PostgreSQL message persistence for Kafka and RabbitMQ profiles; the in-memory profile deliberately skips external persistence.
- Orders appends aggregate events and `OrderIntegrationOutbox` rows in the same Dapper/Npgsql transaction through `IOrderEventCommitter`.
- `OrderIntegrationOutboxRelay` leases committed source-outbox rows, publishes them through Wolverine, and deletes them after publication. A crash after publication and before deletion can redeliver an event, so consumers must remain idempotent.
- The source outbox row `Id` is reused as Wolverine `DeduplicationId` and the `lab-message-id` header on every relay attempt; `AggregateId` is supplied as the partition key.
- Relay claims carry an owner token; failed rows back off per row and park after five attempts for manual inspection/replay.
- `ReserveInventoryUseCase` passes a producer-owned success-event factory to `IInventoryReservationOutbox`; the PostgreSQL adapter privately owns the transaction that commits reservation state, outcome, and `InventoryIntegrationOutbox.Id = OperationId` once.
- `DecreaseStock`, `IncreaseStock`, and `Restock` pass the mutated aggregate, expected prior stock, and producer-owned message to `IInventoryStockOutbox`. The PostgreSQL adapter updates only when the prior stock still matches and inserts the outbox row in the same transaction.
- `InventoryIntegrationOutboxRelay` supports decreased, increased, and returned events, uses the stored normalized ProductId partition key, preserves event occurrence time, marks `PublishedAt` after success, and parks after five failures. A crash after transport publication but before `PublishedAt` can redeliver, so consumers remain idempotent.
- Published rows are retained without limit by default. Change only `Messaging:OutboxRelay:Retention:Mode` (`RetainAll` or `PublishedForDays`) and, for finite retention, a positive `Messaging:OutboxRelay:Retention:PublishedRetentionDays`. The finite policy never removes unpublished or parked rows.
- `Messaging:Profile=InMemory` is the automated-test profile: external transports and Wolverine PostgreSQL persistence are not configured, local queues are used, and `Messaging:OutboxRelay:Enabled=false` disables database polling.
- `Messaging:Profile` accepts only `InMemory`, `Kafka`, or `RabbitMq`. Kafka requires `Messaging:Kafka:ConnectionString`; RabbitMQ requires an absolute `amqp` or `amqps` URI at `Messaging:RabbitMq:ConnectionString`. Missing or unknown values fail during startup configuration.
- Inventory reservation transient persistence failures retry after 100 ms, 500 ms, and 2 seconds, then move to Wolverine's error queue.
- Reservation outcomes are keyed by the caller-provided stable operation ID. Successful replay reuses the same outbox row instead of publishing synchronously or creating a new logical identity.
- Broker-specific physical error queue/topic naming remains implicit in Wolverine transport conventions and requires runtime verification.

Current maintainer rule:

- treat delivery as at-least-once
- assume duplicate delivery is possible
- do not assume replay safety unless the consumer logic is explicitly idempotent
- for Kafka, use one stable producer-selected partition key per ordering scope; do not infer global ordering across partitions
- for independent broadcast-style subscribers, use distinct Kafka consumer groups

## Operational Risks

- The native Orders and Inventory source outboxes close their code-level commit-to-enqueue gaps, but the external PostgreSQL failure-injection gate remains open until rollback and recovery run successfully.
- Kafka and RabbitMQ both route reservation requests to `inventory.requests` and return responses through Wolverine's request reply endpoint (`orders.outbound.replies` on the Orders side). This topology still requires the maintainer's explicit broker runtime verification.
- RabbitMQ logical names are explicit, but the current shared queue configuration is competing-consumer topology. The dual-broadcast direction is authorized, but implementation is not: it still requires an exchange plus separate bound queues and a delivery ledger keyed by message plus destination. Reusing the current single `PublishedAt` would make partial Kafka/RabbitMQ success indistinguishable and is prohibited.
- Product consumer currently listens to `orders.integration.events`, but the business purpose is not yet documented in a matching handler map.

## Orders Schema Upgrade

Fresh Docker volumes receive the current schema from `docker-compose/sql-script/create_orders_table.sql`.
Existing volumes must apply the idempotent migration before the upgraded Orders host starts:

```powershell
Get-Content -Raw docker-compose/sql-script/migrations/orders/20260714_0001_add_order_integration_outbox.sql |
  docker exec -i postgres-order psql -U user -d orders_db
```

The Orders runtime role also needs permission to create and use Wolverine's `wolverine_messages` schema during environment provisioning. Production deployments should apply reviewed Wolverine-generated schema changes with a migration-capable role instead of granting ongoing DDL permission to the application role.

## Inventory Schema Upgrade

Fresh Docker volumes receive the reservation operation and Inventory source-outbox tables from `docker-compose/sql-script/create_inventoryitems_table.sql`.
Existing volumes must apply both idempotent migrations before enabling durable reservation handling and relay:

```powershell
Get-Content -Raw docker-compose/sql-script/migrations/inventory/20260714_0001_add_inventory_reservations.sql |
  docker exec -i postgres-inventory psql -U user -d inventory_db

Get-Content -Raw docker-compose/sql-script/migrations/inventory/20260827_0002_add_inventory_integration_outbox.sql |
  docker exec -i postgres-inventory psql -U user -d inventory_db
```

The Inventory runtime role needs permission to create and use Wolverine's `wolverine_messages` schema under Kafka and RabbitMQ profiles. Production deployments should apply reviewed schema changes with a migration-capable role.
- The product event channel is configured on producer and consumer runtimes, but current Product use cases do not publish a confirmed product integration event.
- Inventory and Products retain dual-profile code, but Kafka is canonical and RabbitMQ parity is not assumed. Runtime drift is a deferred compatibility risk.

## Deferred Items

- exact RabbitMQ exchange, per-consumer queue, binding, and DLQ map for the selected dual-broadcast direction
- `InventoryIntegrationOutboxDelivery`-style per-destination schema, migration, publisher routing, and partial-success recovery policy
- broker-specific dead-letter queue/topic naming
- replay procedures
- confirmed consumer ownership matrix per channel
- Inventory source-outbox retention/archive policy after `PublishedAt`

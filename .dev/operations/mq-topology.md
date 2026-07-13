# MQ Topology

## Scope

This document records the message-bus topology that is explicitly visible in current Wolverine configuration.

It distinguishes between:

- known, code-backed Kafka topic names
- known, code-backed RabbitMQ queue names
- unresolved routing behavior that still depends on Wolverine conventions or future runtime review

## Broker Inventory

| Broker Type | Logical Channel | Producer | Consumer | Purpose |
| --- | --- | --- | --- | --- |
| Kafka | `orders.integration.events` | `SaleOrders.WebApi` | `SaleProducts.Consumer`, `InventoryControl.Consumer`, other listeners | order lifecycle integration stream |
| Kafka | `inventory.requests` | `SaleOrders.WebApi` | `InventoryControl.WebApi` | request/reply inventory reservation |
| Kafka | `orders.outbound.replies` | Wolverine reply channel used by `Orders` | `SaleOrders.WebApi` | reply inbox for reservation flow |
| Kafka | `inventory.integration.events` | `InventoryControl.WebApi` | downstream listeners | stock change integration stream |
| Kafka | `products.integration.events` | configured by `SaleProducts.WebApi`; no confirmed current producer use case | `SaleOrders.Consumer` and possible downstream listeners | configured route, not a confirmed active product integration stream |
| RabbitMQ | `orders.integration.events` | `SaleOrders.WebApi` | `SaleProducts.Consumer`, `InventoryControl.Consumer`, other listeners | RabbitMQ variant of order lifecycle stream |
| RabbitMQ | `inventory.requests` | `SaleOrders.WebApi` | no current `InventoryControl.WebApi` RabbitMQ listener | broken/unconfigured reservation request flow |
| RabbitMQ | `orders.outbound.replies` | Wolverine reply channel used by `Orders` | `SaleOrders.WebApi` | reply inbox for reservation flow |
| RabbitMQ | `inventory.integration.events` | `InventoryControl.WebApi` | downstream listeners | RabbitMQ variant of stock change stream |
| RabbitMQ | `products.integration.events` | configured by `SaleProducts.WebApi`; no confirmed current producer use case | `SaleOrders.Consumer` and possible downstream listeners | configured route, not a confirmed active product integration stream |

## Route Map

| Source Message | Source Context | Broker Object | Destination | Behavior Summary |
| --- | --- | --- | --- | --- |
| `OrderPlaced`, `OrderShipped`, `OrderDelivered`, `OrderCancelled` | `Orders` | `orders.integration.events` | product/inventory consumers and other listeners | durable outbox on publish; consumer inbox on listeners |
| `ReserveInventoryRequestContract` | `Orders` | `inventory.requests` | `Inventory` request contract handler | request/reply flow through Wolverine `InvokeAsync` |
| `ReserveInventoryResponseContract` | `Inventory` | `orders.outbound.replies` or Wolverine reply path | `Orders` caller | used as reply path for reservation result |
| `ProductStockDecreasedIntegrationEvent`, `ProductStockIncreasedIntegrationEvent`, `ProductStockReturnedIntegrationEvent` | `Inventory` | `inventory.integration.events` | downstream listeners | durable outbox on publish |
| future product integration events implementing `IIntegrationEvent` | `Products` | `products.integration.events` | downstream listeners | route is configured with durable outbox, but no current Product use case confirms publication |

## Retry / Dead-Letter Strategy

Known from current code:

- Kafka listeners use durable inbox where configured.
- RabbitMQ listeners use durable inbox where configured.
- publish routes use durable outbox for integration streams and request messages.
- `SaleOrders.WebApi` configures Wolverine PostgreSQL message persistence in the Orders database.
- Orders appends aggregate events and `OrderIntegrationOutbox` rows in the same Dapper/Npgsql transaction through `IOrderEventCommitter`.
- `OrderIntegrationOutboxRelay` leases committed source-outbox rows, publishes them through Wolverine, and deletes them after publication. A crash after publication and before deletion can redeliver an event, so consumers must remain idempotent.
- The source outbox row `Id` is reused as Wolverine `DeduplicationId` and the `lab-message-id` header on every relay attempt; `AggregateId` is supplied as the partition key.
- Relay claims carry an owner token; failed rows back off per row and park after five attempts for manual inspection/replay.
- `QUEUE_SERVICE=InMemory` is the automated-test profile: external transports and Wolverine PostgreSQL persistence are not configured, local queues are used, and `Messaging:OutboxRelay:Enabled=false` disables database polling.
- explicit dead-letter destinations are not yet documented in code-level runtime docs.
- explicit retry counts or backoff classes are not yet documented in these runtime files.

Current maintainer rule:

- treat delivery as at-least-once
- assume duplicate delivery is possible
- do not assume replay safety unless the consumer logic is explicitly idempotent

## Operational Risks

- `SaleOrders.WebApi` contains an inline comment saying the reply listener configuration is incorrect and should only publish requests, not listen to them.
- The native Orders source outbox closes the code-level commit-to-enqueue gap, but DEV-005 remains open until a PostgreSQL failure-injection test proves rollback and recovery behavior.
- `InventoryControl.WebApi` listens to `inventory.requests` in Kafka mode only; its RabbitMQ branch does not configure the corresponding listener, so RabbitMQ reservation is currently broken/unconfigured.
- RabbitMQ logical names are explicit, but exchange/binding details are still implicit under Wolverine conventions.
- Product consumer currently listens to `orders.integration.events`, but the business purpose is not yet documented in a matching handler map.

## Orders Schema Upgrade

Fresh Docker volumes receive the current schema from `docker-compose/sql-script/create_orders_table.sql`.
Existing volumes must apply the idempotent migration before the upgraded Orders host starts:

```powershell
psql "postgresql://user:password@localhost:5433/orders_db" `
  -f docker-compose/sql-script/migrations/orders/20260714_0001_add_order_integration_outbox.sql
```

The Orders runtime role also needs permission to create and use Wolverine's `wolverine_messages` schema during environment provisioning. Production deployments should apply reviewed Wolverine-generated schema changes with a migration-capable role instead of granting ongoing DDL permission to the application role.
- The product event channel is configured on producer and consumer runtimes, but current Product use cases do not publish a confirmed product integration event.
- Inventory and Products both support dual-broker configuration; runtime drift between Kafka and RabbitMQ setups is possible if not kept aligned.

## Deferred Items

- explicit RabbitMQ exchange/binding map
- retry count/backoff policy documentation
- dead-letter queue/topic naming
- replay procedures
- confirmed consumer ownership matrix per channel

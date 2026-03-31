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
| Kafka | `products.integration.events` | `SaleProducts.WebApi` | `SaleOrders.Consumer` and possible downstream listeners | product integration stream |
| RabbitMQ | `orders.integration.events` | `SaleOrders.WebApi` | `SaleProducts.Consumer`, `InventoryControl.Consumer`, other listeners | RabbitMQ variant of order lifecycle stream |
| RabbitMQ | `inventory.requests` | `SaleOrders.WebApi` | implicit `InventoryControl` handler routing | RabbitMQ variant of reservation request flow |
| RabbitMQ | `orders.outbound.replies` | Wolverine reply channel used by `Orders` | `SaleOrders.WebApi` | reply inbox for reservation flow |
| RabbitMQ | `inventory.integration.events` | `InventoryControl.WebApi` | downstream listeners | RabbitMQ variant of stock change stream |
| RabbitMQ | `products.integration.events` | `SaleProducts.WebApi` | `SaleOrders.Consumer` and possible downstream listeners | RabbitMQ variant of product integration stream |

## Route Map

| Source Message | Source Context | Broker Object | Destination | Behavior Summary |
| --- | --- | --- | --- | --- |
| `OrderPlaced`, `OrderShipped`, `OrderDelivered`, `OrderCancelled` | `Orders` | `orders.integration.events` | product/inventory consumers and other listeners | durable outbox on publish; consumer inbox on listeners |
| `ReserveInventoryRequestContract` | `Orders` | `inventory.requests` | `Inventory` request contract handler | request/reply flow through Wolverine `InvokeAsync` |
| `ReserveInventoryResponseContract` | `Inventory` | `orders.outbound.replies` or Wolverine reply path | `Orders` caller | used as reply path for reservation result |
| `ProductStockDecreasedIntegrationEvent`, `ProductStockIncreasedIntegrationEvent`, `ProductStockReturnedIntegrationEvent` | `Inventory` | `inventory.integration.events` | downstream listeners | durable outbox on publish |
| product integration events implementing `IIntegrationEvent` | `Products` | `products.integration.events` | downstream listeners | durable outbox on publish |

## Retry / Dead-Letter Strategy

Known from current code:

- Kafka listeners use durable inbox where configured.
- RabbitMQ listeners use durable inbox where configured.
- publish routes use durable outbox for integration streams and request messages.
- explicit dead-letter destinations are not yet documented in code-level runtime docs.
- explicit retry counts or backoff classes are not yet documented in these runtime files.

Current maintainer rule:

- treat delivery as at-least-once
- assume duplicate delivery is possible
- do not assume replay safety unless the consumer logic is explicitly idempotent

## Operational Risks

- `SaleOrders.WebApi` contains an inline comment saying the reply listener configuration is incorrect and should only publish requests, not listen to them.
- RabbitMQ logical names are explicit, but exchange/binding details are still implicit under Wolverine conventions.
- Product consumer currently listens to `orders.integration.events`, but the business purpose is not yet documented in a matching handler map.
- Inventory and Products both support dual-broker configuration; runtime drift between Kafka and RabbitMQ setups is possible if not kept aligned.

## Deferred Items

- explicit RabbitMQ exchange/binding map
- retry count/backoff policy documentation
- dead-letter queue/topic naming
- replay procedures
- confirmed consumer ownership matrix per channel

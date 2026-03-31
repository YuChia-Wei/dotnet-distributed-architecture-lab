# Context Map

## Scope

This document captures the current bounded-context relationship map for the active distributed commerce sample in this repository.

It is limited to relationships that can be traced back to:

- `.dev/requirement/distributed-commerce-bounded-context-overview.md`
- `.dev/specs/domains/`
- `src/BC-Contracts/`
- current Wolverine routing and consumers under `src/`

## Bounded Context List

| Bounded Context | Core Responsibility | Primary Aggregates / Use Cases | Owned Contracts / Events |
| --- | --- | --- | --- |
| `Products` | Manage sellable product catalog data | `Product`, `CreateProduct`, `UpdateProduct`, `DeleteProduct` | publishes product integration events to `products.integration.events` |
| `Orders` | Manage order placement and lifecycle transitions | `Order`, `PlaceOrder`, `ShipOrder`, `DeliverOrder`, `CancelOrder` | owns `OrderPlaced`, `OrderShipped`, `OrderDelivered`, `OrderCancelled` |
| `Inventory` | Manage available stock and stock adjustments | `InventoryItem`, `DecreaseStock`, `IncreaseStock`, `Restock` | owns `ReserveInventoryRequestContract` handling and stock integration events |

## Relationship Map

| Source Context | Target Context | Interaction Purpose | Interaction Mechanism | Ownership Rule | Failure Sensitivity |
| --- | --- | --- | --- | --- | --- |
| `Orders` | `Inventory` | Reserve stock before confirming order placement | request/reply via `ReserveInventoryRequestContract` and `ReserveInventoryResponseContract` | request contract is owned in `BC-Contracts.Inventory`; `Orders` is caller, `Inventory` is handler | high; failed reservation blocks order placement |
| `Orders` | external downstream consumers | broadcast order lifecycle changes | integration events on `orders.integration.events` | `Orders` owns event semantics and schema | medium to high; downstream views may become stale if delivery fails |
| `Inventory` | external downstream consumers | broadcast stock changes | integration events on `inventory.integration.events` | `Inventory` owns event semantics and schema | high for downstream stock-dependent behaviors |
| `Products` | external downstream consumers | broadcast product changes | integration events on `products.integration.events` | `Products` owns event semantics and schema | medium; current consumer purpose is not fully documented |
| `Product Consumer` runtime | `Orders` events | receive order lifecycle stream | consumer listens to `orders.integration.events` | actual handler intent needs clarification | medium; listener exists but business ownership is still unclear |
| `Inventory Consumer` runtime | `Orders` events | receive order lifecycle stream | consumer listens to `orders.integration.events` | actual handler intent needs clarification | medium; part of current runtime topology but not fully documented |

## Integration Rules

- Cross-bounded-context communication must be MQ-only.
- `Orders` must not reserve inventory through direct HTTP calls.
- Shared contracts belong under `src/BC-Contracts/`, not inside a single bounded context.
- Eventual consistency is expected for inter-context propagation.
- Runtime documentation must distinguish clearly between:
  - active, code-backed routes
  - legacy or unclear routes that still exist in runtime configuration

## Ownership Notes

- `Orders` is the upstream owner of order lifecycle facts.
- `Inventory` is the upstream owner of stock availability facts.
- `Products` is the upstream owner of product catalog facts.
- The request/reply reservation contract is an explicit customer-supplier relationship from `Orders` to `Inventory`.
- Consumer runtimes that listen to a topic without clear documented business handling should be treated as review candidates, not silently assumed to be correct.

## Open Questions / Deferred Decisions

- The exact business purpose of the current `Product` and `Inventory` consumer listeners on `orders.integration.events` needs clarification.
- Whether `Products` currently emits meaningful business integration events beyond infrastructure support still needs to be documented from code or contracts.
- Detailed upstream/downstream consumer ownership beyond the three active contexts should be expanded in later Stage 5 slices.

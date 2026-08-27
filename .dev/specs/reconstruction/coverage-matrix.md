# Reconstruction Coverage Matrix

## Reading Rule

`covered` means a durable normative spec exists. `partial` means some behavior is described but reconstruction-critical details are missing. `gap` and `deferred` are non-passing.

## Product And Runtime Inventory

| Surface | Required inventory | Coverage after this workflow | Evidence / target artifact |
| --- | ---: | --- | --- |
| Product projects | 22 | covered | `project-manifest.json` |
| Test projects | 5 | covered | five independently owned test projects in the manifest |
| Bounded contexts | 3 | covered | system blueprint and domain specs |
| Aggregates | Product, Order, InventoryItem | covered | domain entity specs |
| Runtime hosts | 3 Web APIs + 3 Consumers | covered | `runtime-contracts.json` |
| Databases | Products, Orders, Inventory | covered | `persistence-contracts.json` |
| Broker profiles | InMemory, canonical Kafka, deferred RabbitMq compatibility | covered selection; RabbitMQ physical topology deferred | `runtime-contracts.json`, `message-contracts.json` |
| Observability | logs, traces, metrics via OTLP | covered | runtime contract |

## Use Cases

| Context | Use case | Kind | Production spec | Existing executable oracle | Status |
| --- | --- | --- | --- | --- | --- |
| Products | CreateProduct | command | `../domains/product/usecase/create-product.json` | Product aggregate test | covered |
| Products | UpdateProduct | command | `../domains/product/usecase/update-product.json` | Product aggregate test | covered |
| Products | DeleteProduct | command | `../domains/product/usecase/delete-product.json` | aggregate + use-case test | covered |
| Products | GetAllProducts | query | `../domains/product/usecase/get-all-products.json` | use-case test | covered |
| Products | GetProductById | query | `../domains/product/usecase/get-product-by-id.json` | not-found use-case test | covered |
| Orders | PlaceOrder | command | `../domains/order/usecase/place-order.json` | use-case + CBF | covered |
| Orders | ShipOrder | command | `../domains/order/usecase/ship-order.json` | aggregate theory; use-case-specific executable gap | partial |
| Orders | DeliverOrder | command | `../domains/order/usecase/deliver-order.json` | aggregate theory; use-case-specific executable gap | partial |
| Orders | CancelOrder | command | `../domains/order/usecase/cancel-order.json` | aggregate + use-case tests | covered |
| Orders | GetOrderDetails | query | `../domains/order/usecase/get-order-details.json` | HTTP integration test | covered |
| Inventory | InitProductStock | command | `../domains/inventory-item/usecase/init-product-stock.json` | planned test spec | covered spec / test gap |
| Inventory | IncreaseStock | command | `../domains/inventory-item/usecase/increase-stock.json` | use-case test | covered |
| Inventory | DecreaseStock | command | `../domains/inventory-item/usecase/decrease-stock.json` | success/failure/no-side-effect tests | covered |
| Inventory | Restock | command | `../domains/inventory-item/usecase/restock.json` | use-case test | covered |
| Inventory | ReserveInventory | command | `../domains/inventory-item/usecase/reserve-inventory.json` | idempotency tests + CBF | covered |
| Inventory | GetAvailableQuantity | query | `../domains/inventory-item/usecase/get-available-quantity.json` | planned test spec | covered spec / test gap |

## HTTP Endpoints

The authoritative request/response/status mapping is `http-api-contracts.json` and the three domain adapter specs.

| Context | Endpoints | Count | Status |
| --- | --- | ---: | --- |
| Products | create, list, get by ID, update, delete | 5 | covered |
| Orders | create, get details, ship, deliver, cancel | 5 | covered |
| Inventory | initialize, get quantity, increase, decrease, restock | 5 | covered |

## Messaging

| Contract / channel | Status | Remaining gap |
| --- | --- | --- |
| ReserveInventory request/reply | covered | broker runtime verification remains environment-dependent |
| Orders lifecycle events | covered | consumer business ownership not fully documented |
| Inventory stock events | covered | increase/return names corrected by owner decision; other commands still use direct publish |
| Orders source outbox relay | covered | PostgreSQL failure-injection proof remains required |
| Inventory reservation source outbox relay | covered | real PostgreSQL atomic rollback proof remains required |
| Product integration route | deferred | no confirmed producer use case |
| RabbitMQ compatibility topology | deferred | shared queues are not broadcast; exchange/per-consumer queue/binding/DLQ and promotion decision deferred |

## Persistence

| Store | Required behavior | Status |
| --- | --- | --- |
| Products | state row, soft delete, optimistic version | covered |
| Orders event store | ordered unique stream versions, JSON event map | covered |
| Orders read model | projection upsert in source transaction | covered |
| Orders source outbox | atomic insert, lease/backoff/park/stable identity | covered spec; failure-injection gate open |
| Inventory items | unique product, stock state | covered with positive-quantity quality uplift |
| Inventory reservation operations | durable idempotency outcome | covered |
| Inventory reservation source outbox | atomic insert with state/outcome, stable identity, retained PublishedAt, lease/backoff/park | covered spec; external rollback gate open |

## Current Executable Oracle Inventory

- Product aggregate: constructor/update/delete events and invalid input.
- Product use cases: delete persistence, get-all query service, get-by-id not-found.
- Order aggregate: reason propagation, same-state no-op, missing reason, replay cleanliness, commit acknowledgement and mismatch.
- Order placement: reservation success atomic commit and reservation failure no commit.
- Order cancellation: state/event commit and same-state skip.
- Order query/API: get-details payload.
- Orders relay: stable logical identity across retries and duplicate publishes.
- Inventory commands: decrease success, insufficient/missing no side effects, increase, restock.
- Reservation: validation, replay, payload conflict, terminal failure replay, atomic in-memory staging, stage-failure no-commit, stable relay retry identity/timestamp, cancellation, and retry policy.
- Inventory event contracts: corrected increase/return quantity JSON names and outbox occurrence-time round trip.
- Messaging options: InMemory, missing Kafka connection, invalid RabbitMQ URI, unknown profile.

## Non-Passing Gaps

1. ShipOrder and DeliverOrder lack direct use-case tests even though aggregate behavior is covered.
2. InitProductStock and GetAvailableQuantity lack executable tests.
3. Product create/update use-case orchestration is not directly tested.
4. Product hosts use legacy broker configuration in current implementation; reconstruction must use the shared profile contract.
5. Consumer subscriptions do not map to clear business handlers.
6. PostgreSQL failure injection has not yet proven Orders source transaction rollback/recovery.
7. The Inventory PostgreSQL concurrency test is checked in but remains non-passing evidence until an opted-in run succeeds.
8. Product integration event production and subscribed consumer business ownership need owner decisions.
9. RabbitMQ promotion/dual-deployment and physical broadcast/DLQ topology remain owner-deferred; they are not canonical Kafka blockers.
10. The Inventory outbox external test proves successful-row insertion when PostgreSQL runs, but failure injection must still prove state/outcome/outbox rollback together.
11. Two independent LUNA-class clean-room reconstructions have not run.

## Readiness Rule

The specification baseline may be complete while implementation/testing gaps remain. A future reconstructed system is not accepted until every normative row is covered, canonical PostgreSQL/Kafka gates pass, and two isolated LUNA-class reconstructions independently pass the same external-contract comparison. `blocked-by-environment` is not passed, and acceptance never authorizes deletion of the original source.

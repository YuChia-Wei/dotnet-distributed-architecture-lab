# Reconstruction Coverage Matrix

## Reading Rule

`covered` means a durable normative spec exists. `partial` means some behavior is described but reconstruction-critical details are missing. `gap` and `deferred` are non-passing.

## Product And Runtime Inventory

| Surface | Required inventory | Coverage after this workflow | Evidence / target artifact |
| --- | ---: | --- | --- |
| Product projects | 22 | covered | `project-manifest.json` |
| Sample projects | 3 | covered | separate EF Core/Wolverine Application, Infrastructure, and Host |
| Test projects | 6 | covered | five product/domain projects and one sample test project in the manifest |
| Bounded contexts | 3 | covered | system blueprint and domain specs |
| Aggregates | Product, Order, InventoryItem | covered | domain entity specs |
| Product runtime hosts | 3 Web APIs + 3 Consumers | covered | `runtime-contracts.json` |
| Sample host | 1 | covered | separate EF Core/Wolverine sample in `project-manifest.json` |
| Databases | Products, Orders, Inventory | covered | `persistence-contracts.json` |
| Broker profiles | InMemory, canonical Kafka, RabbitMq compatibility, target dual broadcast | current single-profile selection covered; dual-destination state and RabbitMQ physical fanout deferred | `runtime-contracts.json`, `message-contracts.json` |
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
| Orders | ShipOrder | command | `../domains/order/usecase/ship-order.json` | aggregate theory and historical commerce success; direct use-case test gap | partial |
| Orders | DeliverOrder | command | `../domains/order/usecase/deliver-order.json` | aggregate theory and historical commerce success; direct use-case test gap | partial |
| Orders | CancelOrder | command | `../domains/order/usecase/cancel-order.json` | aggregate + use-case tests | covered |
| Orders | GetOrderDetails | query | `../domains/order/usecase/get-order-details.json` | HTTP integration test | covered |
| Inventory | InitProductStock | command | `../domains/inventory-item/usecase/init-product-stock.json` | historical commerce success and repository tests; direct use-case test gap | covered spec / partial execution |
| Inventory | IncreaseStock | command | `../domains/inventory-item/usecase/increase-stock.json` | use-case test | covered |
| Inventory | DecreaseStock | command | `../domains/inventory-item/usecase/decrease-stock.json` | success/failure/no-side-effect tests | covered |
| Inventory | Restock | command | `../domains/inventory-item/usecase/restock.json` | use-case test | covered |
| Inventory | ReserveInventory | command | `../domains/inventory-item/usecase/reserve-inventory.json` | idempotency tests + CBF | covered |
| Inventory | GetAvailableQuantity | query | `../domains/inventory-item/usecase/get-available-quantity.json` | historical commerce success and repository tests; direct use-case test gap | covered spec / partial execution |

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
| Inventory stock events | covered in source outbox | decrease/increase/return are atomically staged; increase/return names corrected by owner decision |
| Orders source outbox relay | covered | PostgreSQL failure-injection proof remains required |
| Inventory reservation source outbox relay | covered | PostgreSQL rollback and concurrency passed at the dated subject below; later changes require fresh execution |
| Product diagnostic route | implemented | enabled diagnostic producers and Orders handlers; historical parallel-work execution below |
| Product business integration events | deferred | no confirmed business producer or consumer reaction |
| RabbitMQ compatibility topology | target direction selected / implementation deferred | shared queues are not broadcast; exchange/per-consumer queue/binding/DLQ and per-destination outbox state remain open |

## Persistence

| Store | Required behavior | Status |
| --- | --- | --- |
| Products | state row, soft delete, optimistic version | covered |
| Orders event store | ordered unique stream versions, JSON event map | covered |
| Orders read model | projection upsert in source transaction | covered |
| Orders source outbox | atomic insert, lease/backoff/park/stable identity | covered spec; failure-injection gate open |
| Inventory items | unique product, stock state | covered with positive-quantity quality uplift |
| Inventory reservation operations | durable idempotency outcome | covered |
| Inventory reservation source outbox | atomic insert with state/outcome, stable identity, retained PublishedAt, lease/backoff/park | covered spec; PostgreSQL rollback passed at the dated subject below |

## Current Executable Oracle Inventory

- Product aggregate: constructor/update/delete events and invalid input.
- Product use cases: delete persistence, get-all query service, get-by-id not-found.
- Order aggregate: reason propagation, same-state no-op, missing reason, replay cleanliness, commit acknowledgement and mismatch.
- Order placement: reservation success atomic commit and reservation failure no commit.
- Order cancellation: state/event commit including event type and reason, and same-state skip; direct not-found coverage remains a gap.
- Order query/API: get-details payload.
- Orders relay: stable logical identity, payload and original occurrence time across retries and duplicate publishes; all four integration-event types have JSON round-trip and producer-constructor compatibility tests.
- Inventory commands: decrease success, insufficient/missing no side effects, increase, restock.
- Inventory EF persistence: existing-schema mapping, scoped registrations, no-tracking read projection, new-item persistence, expected-stock concurrency, and state/outcome/outbox rollback in opt-in PostgreSQL tests.
- Reservation: validation, replay, payload conflict, terminal failure replay, atomic in-memory staging, stage-failure no-commit, stable relay retry identity/timestamp, cancellation, and retry policy.
- Inventory event contracts: corrected increase/return quantity JSON names and outbox occurrence-time round trip.
- Messaging options: InMemory, missing Kafka connection, invalid RabbitMQ URI, unknown profile.

## Non-Passing Gaps

1. ShipOrder and DeliverOrder lack direct use-case tests even though aggregate behavior is covered.
2. InitProductStock and GetAvailableQuantity lack direct use-case tests; historical positive commerce and repository tests do not cover all validation/not-found cases.
3. Product create/update use-case orchestration is not directly tested.
4. Product hosts use legacy broker configuration in current implementation; reconstruction must use the shared profile contract.
5. Consumer subscriptions do not map to clear business handlers.
6. PostgreSQL failure injection has not yet proven Orders source transaction rollback/recovery.
7. Product business integration event production and subscribed consumer business ownership need owner decisions; executable diagnostics do not resolve them.
8. Kafka + RabbitMQ dual broadcast is the owner-selected target direction; per-destination delivery schema, physical fanout/DLQ topology, and runtime proof remain incomplete and are not canonical Kafka blockers.
9. Two independent LUNA-class clean-room reconstructions have not run.

## Observed Execution — 2026-09-21

This is historical execution evidence for commit `edd18d70a94da99e0548de986227655ec102a145`, from `2026-09-21T01:21:35.087080Z` to `2026-09-21T01:23:09.825269Z`. It is not a claim that later source changes or a source-free reconstruction have passed.

- The explicit Docker/PostgreSQL/Kafka validation completed with exit code 0: **122 passed, 0 failed, 0 skipped**. Project counts were EF Core/Wolverine sample 16, Inventory 47, Orders domain 13, Orders application/integration 11, Products domain 9, and Products application/integration 26.
- Opted-in Inventory PostgreSQL tests exercised concurrent reservations, duplicate/conflicting operation identities, terminal-outcome replay, invalid-message rollback of stock/operation/outbox, expected-stock conflicts, and rollback/retry persistence. This resolves the earlier absence of executed Inventory concurrency/rollback evidence for this subject; it does not establish every future failure mode or replay-after-retention behavior.
- Commerce verification passed Product create/read, Inventory seed/read, Kafka stock reservation, Order read, ship/deliver, cancellation, and insufficient-stock rejection. Positive end-to-end flows do not replace direct use-case validation/not-found tests or Orders PostgreSQL failure injection.
- Both diagnostic parallel-work modes showed overlap and replay deduplication. They are diagnostic examples, not implemented consumer business reactions.

The local evidence bindings are below. These ignored artifacts may be absent from a clean checkout; their recorded hashes identify the inspected evidence, and their absence must not be replaced with an invented pass.

| Evidence artifact | SHA-256 |
| --- | --- |
| `artifacts/inventory-efcore/validation-04-completion.json` | `3c59c3b0279a9ed7cd98ea9b8717ef5123fd58c87a5e1623179d406d5b3c7ad2` |
| `artifacts/inventory-efcore/validation-04-runner-receipt.json` | `ee63d18b5069e304b5301d1409c5d17ab519cc67539821fe0609f43fc5bd4a33` |
| `artifacts/inventory-efcore/validation-04-test-summary.json` | `4769f0ae4110a46ee116e998ee5a9490ba92399bd6b46f005635ad9e256a0eaf` |
| `artifacts/inventory-efcore/validation-04-commerce.json` | `3a2fd3b10af49dc58c48fa02d2235d75d12c82b1d5d5b20639aeb622e293d7d7` |
| `artifacts/inventory-efcore/validation-04-parallel.json` | `ae4b5d7d8319738d70aa1794d8a6d48c75495c000b2f2fd01f90e970d7d79469` |

## Readiness Rule

The specification baseline may be complete while implementation/testing gaps remain. A future reconstructed system is not accepted until every normative row is covered, canonical PostgreSQL/Kafka gates pass, and two isolated LUNA-class reconstructions independently pass the same external-contract comparison. `blocked-by-environment` is not passed, and acceptance never authorizes deletion of the original source.

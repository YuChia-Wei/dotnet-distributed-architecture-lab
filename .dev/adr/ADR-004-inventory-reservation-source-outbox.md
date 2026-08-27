# ADR-004: Inventory Reservation Source Outbox

## Status

Accepted

## Date

2026-08-27

## Context

`ReserveInventory` previously committed the PostgreSQL reservation transaction and then published `ProductStockDecreasedIntegrationEvent`. A process failure between those operations could leave durable stock reduction without any recoverable outgoing event. Retrying reused a stable identity, but only if an upstream caller retried; it did not close the permanent-loss window.

The event contract is a producer business decision, while SQL transactions, serialization, leasing, and broker delivery are Infrastructure mechanics. The architecture must preserve that ownership boundary and make the strong-consistency requirement visible to the use case.

## Decision

- `ReserveInventoryUseCase` depends on the capability-specific `IInventoryReservationTransactionFactory` and `IInventoryReservationTransaction` Application ports.
- The use case validates input, resolves the reservation, creates `ProductStockDecreasedIntegrationEvent` on success, stages it with stable delivery metadata, and commits explicitly.
- The PostgreSQL adapter writes stock, terminal reservation outcome, and `InventoryIntegrationOutbox` in one local transaction. Failure before commit rolls all three back.
- `InventoryIntegrationOutbox.Id` equals `OperationId`; replay uses `ON CONFLICT DO NOTHING` and cannot create a second logical event.
- The relay publishes at least once with the stored partition key, marks `PublishedAt`, retains the row as delivery evidence, retries with bounded backoff, and parks after five failures.
- This decision applies only to `ReserveInventory`. Other Inventory commands retain their current direct-publish path until separately migrated and tested.

## Consequences

### Positive

- The commit-to-enqueue loss window is closed for Inventory reservation.
- Producer event decisions remain in Application while broker mechanics stay in Infrastructure.
- Stable identity, replay, retry, and operator evidence are explicit and testable.

### Negative

- The use case exposes an explicit transaction lifecycle and therefore has more orchestration code.
- Published rows accumulate until a retention/archive policy is selected.
- Direct-publish and source-outbox patterns temporarily coexist inside Inventory.

### Follow-up

- Run the opt-in PostgreSQL concurrency and failure-injection gate; skipped execution is non-passing.
- Observe the concrete transaction-port design before deciding whether to simplify or extend it.
- Define retention/archive and manual replay procedures.
- Evaluate separate bounded migrations for IncreaseStock, DecreaseStock, and Restock.

## Notes

This is a provisional accepted implementation direction: the owner explicitly reserved the right to adjust it after reviewing the actual code architecture.

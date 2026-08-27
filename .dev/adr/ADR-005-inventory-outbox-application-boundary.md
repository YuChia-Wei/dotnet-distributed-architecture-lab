# ADR-005: Inventory Outbox Application Boundary

## Status

Accepted

## Date

2026-08-27

## Context

Inventory must never durably change stock and then lose the corresponding integration event because a process stops between database save and broker publish. The previous reservation slice closed that gap, but exposed `Begin`, `Stage`, and `Commit` transaction lifecycle methods to Application code. The other stock-changing commands still saved state and published directly.

Transactional Outbox and Unit of Work solve different problems. Outbox makes state plus publication intent atomic. Unit of Work coordinates a local transaction. They can be used together, but a generic Application `IUnitOfWork` would expose a broader abstraction than the current invariant requires: every current operation changes one Inventory capability/aggregate plus its outgoing message.

The owner also selected Kafka + RabbitMQ dual broadcast as a likely target and chose unlimited retention for now, with an explicit future adjustment point.

## Decision

- Application depends on capability-specific outbox ports, not database transaction lifecycle or a generic Unit of Work.
- `IInventoryReservationOutbox.ReserveAndStageAsync` owns the atomic reservation operation. `ReserveInventoryUseCase` supplies a factory that creates the producer-owned success event; Infrastructure invokes it only for a successful outcome and commits state, outcome, and outbox once.
- `IInventoryStockOutbox.SaveAndStageAsync` atomically updates one existing `InventoryItem` and inserts one producer-created message for `DecreaseStock`, `IncreaseStock`, or `Restock`. The expected pre-mutation stock is part of the port contract and PostgreSQL update predicate, so a concurrent change fails closed instead of being overwritten.
- `InitProductStock` does not use the outbox because it has no specified outgoing integration event.
- Infrastructure may implement either port with a local transaction or internal Unit of Work. Those types remain adapter-private.
- The Inventory relay supports decreased, increased, and returned event types. It uses stored message identity and `ProductId.ToString("N")` partition key, retries with bounded backoff, and parks after five failures.
- Published rows default to unlimited retention through `Messaging:OutboxRelay:Retention:Mode=RetainAll`. The only supported finite policy is `PublishedForDays` with a positive `Messaging:OutboxRelay:Retention:PublishedRetentionDays`. Unpublished and parked rows are not removed by this policy.
- Kafka remains the implemented canonical destination. Dual Kafka + RabbitMQ broadcast is a target direction, not a present capability. Before activation, the single `PublishedAt` completion field must evolve to per-destination delivery state, and RabbitMQ must use an exchange with a separate queue per independent subscriber.

## Why A Generic Unit Of Work Is Not Used

A generic Unit of Work becomes justified when one use case coordinates multiple aggregates or repositories under a named all-or-nothing business invariant. The current Inventory commands do not meet that threshold. Publishing a message is a durability requirement of the same business operation, so the narrow outbox port communicates more intent and gives a lower-cost reconstruction model fewer invalid choices.

## Consequences

### Positive

- No Inventory event-producing command has a direct publish-after-save loss window.
- Application code expresses producer meaning while Infrastructure owns SQL, serialization, and transaction mechanics.
- Expected-stock comparison prevents silent lost updates for ordinary stock commands.
- Retention is safe by default and has one typed, validated adjustment point.
- Future dual-broker work has an explicit prerequisite instead of reusing an invalid single-completion flag.

### Negative

- Commands without caller-supplied operation IDs remain non-idempotent across whole-request retries; each accepted retry can create a new message and stock mutation.
- PostgreSQL atomicity and concurrency still require opted-in real-database tests; broker-free tests do not prove the external store.
- Dual broadcast requires a schema, publisher-routing, and operational migration slice before it can be enabled.

## Supersedes

- [ADR-004](ADR-004-inventory-reservation-source-outbox.md), whose historical reservation-specific rationale remains valid but whose explicit transaction-port shape and limited command scope are replaced here.

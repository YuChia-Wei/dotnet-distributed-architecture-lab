# ADR-002: Pluggable Durable Messaging Boundary

## Status

Accepted

## Date

2026-07-13

## Context

The repository must demonstrate reliable bounded-context messaging and allow alternative implementations to be compared. Calling Wolverine `UseDurableOutbox` or `UseDurableInbox` without a message store does not establish durability, while publishing after a Dapper event-store commit leaves a commit-to-enqueue crash window.

## Decision

- Application code depends on project-owned messaging and commit ports, never Wolverine types.
- Introduce project-owned source-transaction and integration-event delivery ports; no Application contract exposes Wolverine types.
- The Orders write boundary owns an atomic commit operation that appends Order events and records outgoing messages in one PostgreSQL transaction.
- A native Dapper/PostgreSQL source outbox is the first atomic adapter. Wolverine PostgreSQL persistence owns the subsequent durable relay/delivery stage, while Kafka and RabbitMQ remain separate transport profiles behind the same logical contracts.
- Provide an explicitly non-durable in-memory adapter for deterministic automated tests.
- Kafka and RabbitMQ both support the same business capability, but their topic/partition/group and exchange/queue/binding semantics remain explicit rather than being forced into identical physical topology.
- Real Kafka/RabbitMQ connectivity tests are opt-in/manual. Required automated tests use local/in-memory Wolverine routing and do not start an external broker.

## Consequences

### Positive

- Durability semantics are testable across implementations without coupling Application to Wolverine.
- The lab can compare native PostgreSQL source-outbox, Wolverine persisted delivery, and in-memory strategies.
- Default tests remain deterministic and process-safe.

### Negative

- A persistence provider alone does not prove atomicity with the current Dapper transaction.
- The source transaction and relay recovery behavior require separate database-backed tests; in-memory transport tests cannot prove PostgreSQL atomicity.
- Two transport profiles require separate topology/configuration tests and operational guidance.

### Follow-up

- Contract-test the source transaction and relay in DEV-005, including rollback, stable retry identity, duplicate delivery, and recovery.
- Implement CQRS separation, broker parity/configuration, and reservation idempotency in DEV-010 through DEV-012.
- Own the source-outbox and Wolverine PostgreSQL schemas as separate migration/permission surfaces; do not rely on production startup auto-provisioning.

## Notes

The Product producer is not part of this decision's current implementation scope. `MSG-003` remains a future commercial requirement.

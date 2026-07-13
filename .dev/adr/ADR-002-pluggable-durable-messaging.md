# ADR-002: Pluggable Durable Messaging Boundary

## Status

Accepted

## Date

2026-07-13

## Context

The repository must demonstrate reliable bounded-context messaging and allow alternative implementations to be compared. Calling Wolverine `UseDurableOutbox` or `UseDurableInbox` without a message store does not establish durability, while publishing after a Dapper event-store commit leaves a commit-to-enqueue crash window.

## Decision

- Application code depends on project-owned messaging and commit ports, never Wolverine types.
- Introduce an integration-event outbox port whose success means the message was durably accepted for later delivery.
- The Orders write boundary owns an atomic commit operation that appends Order events and records outgoing messages in one PostgreSQL transaction.
- Wolverine PostgreSQL message persistence is the first durable adapter and Kafka and RabbitMQ remain separate transport profiles behind the same logical contracts.
- An in-memory adapter exists for deterministic automated tests and is explicitly non-durable.
- Kafka and RabbitMQ both support the same business capability, but their topic/partition/group and exchange/queue/binding semantics remain explicit rather than being forced into identical physical topology.
- Real Kafka/RabbitMQ connectivity tests are opt-in/manual. Required automated tests use local/in-memory Wolverine routing and do not start an external broker.

## Consequences

### Positive

- Durability semantics are testable across implementations without coupling Application to Wolverine.
- The lab can compare PostgreSQL/Wolverine, native outbox, and in-memory strategies.
- Default tests remain deterministic and process-safe.

### Negative

- A persistence provider alone does not prove atomicity with the current Dapper transaction.
- The adapter must prove it can enlist envelope persistence in the same Npgsql transaction. If it cannot, a native Dapper outbox adapter is required to close the crash window.
- Two transport profiles require separate topology/configuration tests and operational guidance.

### Follow-up

- Implement and contract-test the ports in DEV-005.
- Implement CQRS separation, broker parity/configuration, and reservation idempotency in DEV-010 through DEV-012.
- Own PostgreSQL schema migrations explicitly; do not rely on production startup auto-provisioning.

## Notes

The Product producer is not part of this decision's current implementation scope. `MSG-003` remains a future commercial requirement.

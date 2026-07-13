# Critical Remediation Architecture Decisions

## Metadata

- `workflow_id`: `2026-07-13-critical-remediation-and-analyzer-integration`
- `task_id`: `DEV-003`
- `owner_skill`: `ddd-ca-hex-architect`
- `status`: `final`
- `created_at`: `2026-07-13T23:40:00+08:00`
- `updated_at`: `2026-07-14T00:09:00+08:00`

## Approved Direction

| Finding | Decision | Execution task |
| --- | --- | --- |
| ARC-001 | After a successful event append, advance the aggregate to the committed version and clear only the committed pending events. Preserve pending events on append failure. | DEV-004 |
| ARC-002 | Allow transitions to any different lifecycle status only with a non-blank reason recorded in events; same-state is a no-op. State mutation occurs only in `When`. | DEV-004 / ADR-001 |
| MSG-001 | Use project-owned source-transaction and delivery ports. The Orders source adapter writes events and outgoing rows in one Dapper/Npgsql transaction; Wolverine PostgreSQL persists the subsequent relay/delivery stage. | DEV-005 / ADR-002 |
| ARC-003 | Separate the aggregate write port from read-only query ports/read models; do not replay all event streams for list queries. | DEV-010 |
| MSG-002 / MSG-005 | Support Kafka and RabbitMQ as distinct profiles with equivalent business capability, typed validated configuration, and complete request/reply topology. | DEV-011 |
| MSG-004 | Add stable reservation operation identity, idempotent consumption, retry/backoff, and terminal failure routing. | DEV-012 |
| MSG-003 | Defer Product producer/event ownership until a future commercial requirement identifies event meaning and consumers. | Future backlog |

## Test Boundary

- Required automated messaging tests use Wolverine local/in-memory queues and stub external transports.
- Real Kafka/RabbitMQ connectivity suites are manual opt-in and excluded from `MQArchLab.slnx`.
- Broker parity means equivalent business capability, not identical ordering or topology semantics.

## Evidence And Limits

- Official Wolverine documentation requires PostgreSQL message persistence plus durable endpoints for inbox/outbox behavior.
- Wolverine documents integrated atomic outbox workflows for EF Core/Marten; no equivalent Dapper transaction enlistment was established during DEV-003.
- DEV-005 selected the ADR-approved native Orders source outbox because Wolverine/Dapper enlistment was not established. Atomicity is between `OrderEvents` and `OrderIntegrationOutbox`; relay handoff is at-least-once and can duplicate after publish-before-delete.
- DEV-005 must retain MSG-001 as unresolved until PostgreSQL failure-injection and relay recovery tests prove the source transaction and stable retry identity.

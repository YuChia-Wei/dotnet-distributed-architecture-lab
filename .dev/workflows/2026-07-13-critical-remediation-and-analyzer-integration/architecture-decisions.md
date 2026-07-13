# Critical Remediation Architecture Decisions

## Metadata

- `workflow_id`: `2026-07-13-critical-remediation-and-analyzer-integration`
- `task_id`: `DEV-003`
- `owner_skill`: `ddd-ca-hex-architect`
- `status`: `final`
- `created_at`: `2026-07-13T23:40:00+08:00`
- `updated_at`: `2026-07-13T23:40:00+08:00`

## Approved Direction

| Finding | Decision | Execution task |
| --- | --- | --- |
| ARC-001 | After a successful event append, advance the aggregate to the committed version and clear only the committed pending events. Preserve pending events on append failure. | DEV-004 |
| ARC-002 | Allow transitions to any different lifecycle status only with a non-blank reason recorded in events; same-state is a no-op. State mutation occurs only in `When`. | DEV-004 / ADR-001 |
| MSG-001 | Use project-owned outbox/commit ports. Wolverine PostgreSQL is the first durable adapter, but it must prove atomic enlistment with the Dapper/Npgsql event-store transaction; persistence configuration alone does not close the failure window. | DEV-005 / ADR-002 |
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
- DEV-005 must retain MSG-001 as unresolved if failure-injection tests cannot prove one transaction across event append and outgoing envelope persistence.

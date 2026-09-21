# Inventory persistence decision

Owner decision: 2026-09-21 user request and Issue #14. Design author: Codex parent. Status: implementation-authorized. Scope: Inventory only.

## Responsibility and consistency

InventoryItem remains a transport/ORM-free aggregate. Application ports, business decisions and typed outcomes remain unchanged. Infrastructure owns EF Core mapping, queries, reservation operation records and outbox records. Products and Orders retain Dapper, including Orders event sourcing.

Use a scoped InventoryDbContext for runtime persistence. Map existing lowercase PostgreSQL tables/columns and existing JSONB/event metadata; do not drop, recreate or rename tables. Existing SQL migrations remain schema authority, including fresh Compose initialization. Do not call EnsureCreated/Migrate on the shared existing database. EF uses current compatible Npgsql/EF package versions from the sample.

The existing capability-specific stock/outbox and reservation/outbox adapters remain the single physical completion owner for their local business transaction. Preserve expected-stock conflict semantics; reservation claims OperationId and locks the inventory row before evaluating stock. Preserve replay/conflicting-payload results, metadata, outbox retry/park/retention and stable delivery IDs. Use EF LINQ/mapping for ordinary persistence; retain parameterized PostgreSQL advisory/row locking or ON CONFLICT SQL through EF when required to preserve concurrency semantics. Never interpolate untrusted SQL structure.

A fresh context/scope owns each background relay unit. The relay may publish only committed records; publishing is at-least-once with stable message IDs. Its independent work cannot join a request transaction by merely sharing a connection string. Rollback must not leave tracked uncommitted records reusable on a later attempt.

## Alternatives and boundaries

Replacing the product source outbox with Wolverine native EF inbox/outbox would also change operation retention, event delivery ownership and API transaction orchestration. That is a broader behavior migration than choosing EF Core, so preserve the existing source-outbox contract in this delivery. The separate sample remains the comparison for Wolverine's native Eager transaction pipeline. The product path does not claim atomic broker acknowledgement and SQL commit, permanent envelope deduplication or exactly-once delivery.

No aggregate boundary, broker topology, public event shape, soft-delete lifecycle or global Unit of Work abstraction changes. Preserve existing physical deletion behavior only where already exposed; no new deletion capability is introduced.

## Acceptance

AC1 Inventory runtime uses EF Core without Dapper imports/direct package dependency; other contexts retain Dapper.
AC2 Existing rows, queries and initialization work against the current schema.
AC3 Stock state and outgoing intent commit together; failures roll back; stale expected stock is rejected.
AC4 Reservation duplicates replay one outcome, payload conflicts reject, concurrent requests cannot oversell, and only one outgoing event is staged.
AC5 Outbox relay retains retry/park/retention, stable delivery metadata and cancellation behavior.
AC6 Real Compose product/inventory/order/Kafka flows pass; existing volumes remain intact.
AC7 v0.18 stays finalized; governance checks pass and final main is pushed and read back.

Official EF reference: https://learn.microsoft.com/en-us/ef/core/saving/transactions and https://learn.microsoft.com/en-us/ef/core/querying/sql-queries . ExecuteUpdate operations require explicit transaction and concurrency predicates when combined with tracked outbox changes: https://learn.microsoft.com/en-us/ef/core/saving/execute-insert-update-delete .

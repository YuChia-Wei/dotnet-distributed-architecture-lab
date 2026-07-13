# .NET Backend Technology Profile

本文件描述這個 reusable context framework 支援的 .NET backend 技術範圍，不強制 target repository 採用特定資料庫、ORM、message broker 或 persistence package。

Target repository 必須由 `repo-structure-sync` 依實際 solution、package references、configuration 與 deployment evidence 建立 `.dev/project-config.yaml`。未確認的技術選擇不得由 framework 預設補入。

## Baseline

| Area | Framework baseline | Target repository decision |
| --- | --- | --- |
| Language/Runtime | Modern C# / supported .NET | Confirm exact version from project files |
| Architecture | DDD + Clean Architecture + CQRS + ports/adapters | Confirm adopted boundaries |
| Command persistence | Aggregate Repository port | Select database, ORM/event store, and adapter |
| Query persistence | `IQueryRepository`-derived ports | Select provider per read model |
| Messaging | MQ-first across bounded contexts | Select RabbitMQ, Kafka, or target-supported broker |
| Testing | xUnit + NSubstitute reference guidance | Confirm packages from target |
| Deployment | Linux container compatible by default | Confirm target deployment |

## Persistence Selection Policy

Normative standards define semantics rather than implementation packages:

- Aggregate persistence accepts Aggregate Roots only.
- Query ports are read-only.
- Capability-specific writers have explicit roles.
- Transaction, optimistic concurrency, event acknowledgement, and outbox atomicity must be defined.
- Technology-specific behavior belongs in conditional implementation guidance.

Supported reference guidance may include:

- EF Core；
- Dapper；
- Npgsql / PostgreSQL；
- document databases；
- event stores；
- in-memory test adapters。

Supporting a technology does not make it mandatory.

## Conditional Technology Concerns

### EF Core

- tracking versus no-tracking policy；
- async terminal operators and materialization；
- model/configuration completeness；
- optimistic concurrency mapping；
- transaction/outbox integration；
- migration ownership。

### Dapper / direct SQL

- connection and transaction lifetime；
- parameterization；
- mapping completeness；
- optimistic concurrency predicates；
- multi-statement atomicity；
- batch/chunk behavior。

### Event store

- expected version；
- append-only event persistence；
- replay and snapshot policy；
- event acknowledgement after successful append。

### Messaging

- delivery guarantee；
- idempotency；
- outbox/inbox；
- retry/dead-letter policy；
- contract compatibility。

## Cross-platform Requirement

除非 target repository 明確選擇其他平台，framework guidance 預設：

- artifacts 可在 Linux container 執行；
- 避免 Windows-only package/API；
- 使用 `Path.Combine()` 或跨平台 path API；
- deployment-specific assumptions 必須由 target evidence 證明。

## Version Ownership

Package/runtime versions屬於 target repository truth。

- 不在 reusable standards 中把 reference version 當成 universal requirement。
- Version examples 必須標示為 reference/template。
- 實作與 validation 應讀取 target project/lock/config files。

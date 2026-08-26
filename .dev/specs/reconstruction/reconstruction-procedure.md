# Reconstruction Procedure

## Preconditions

- Work in a new clean repository or isolated worktree.
- Product source and tests are assumed unavailable.
- Read `README.MD` and the authority order before generating code.
- Pin all implementation work to the requirement/spec versions being used.

## Phase 1 — Skeleton And Dependency Direction

1. Create `global.json`, `MQArchLab.slnx`, and all projects from `project-manifest.json`.
2. Add project references in build order; verify Domain projects have no forbidden outward dependencies.
3. Implement BuildingBlocks behavior with focused tests before any bounded context.
4. Implement Published Language message/DTO contracts exactly as serialized compatibility surfaces.
5. Add empty SharedKernel placeholder without inventing shared concepts.

Exit gate: solution restore/build succeeds with empty bounded-context shells and dependency-direction checks pass.

## Phase 2 — Domain Models

Implement Product, Order, and InventoryItem from entity specs and requirement IDs. Generate tests first from domain test specs. For Order, implement event replay/commit semantics before application use cases. Apply quality-uplift validation to Inventory quantities.

Exit gate: aggregate oracles pass and no Domain project references ASP.NET, Dapper, Npgsql, Wolverine, or BC contracts.

## Phase 3 — Application Ports And Use Cases

Implement the 16 rows in `coverage-matrix.md`. Each use case receives a transport-neutral Input and non-optional cancellation token, depends only on Domain and outbound ports, and returns the specified Output/Result.

Exit gate: all use-case tests pass, including no-side-effect failure paths and same-state no-op behavior.

## Phase 4 — Persistence And Messaging Adapters

1. Create database schemas from `persistence-contracts.json`.
2. Implement Products state repository/query repository.
3. Implement Orders event store, read model, native source outbox, and relay as one durability capability.
4. Implement Inventory aggregate/query repositories and the durable reservation repository.
5. Implement project-owned integration publisher/gateway adapters and stable delivery metadata.

Exit gate: database-backed concurrency, atomicity, idempotency, retry identity, rollback, and replay tests pass.

## Phase 5 — HTTP And MQ Inbound Adapters

Implement the three controllers and reservation handler from adapter/message specs. Use explicit status/error mapping and exactly one use-case invocation per entry. Configure all hosts from the shared runtime contract.

Exit gate: HTTP contract tests and InMemory broker routing tests pass.

## Phase 6 — Hosts, Containers, And Observability

Create three APIs, three Consumers, six Dockerfiles, Compose services, broker/database dependencies, and OTLP telemetry. Kafka and RabbitMQ physical integration tests remain separately selected environment gates.

Exit gate: InMemory hosts start without external broker persistence; Kafka/RabbitMQ profiles fail fast on invalid configuration; container restore layers include recursive project metadata.

## Phase 7 — Acceptance

Run, at minimum:

```text
dotnet restore MQArchLab.slnx
dotnet build MQArchLab.slnx --no-restore
dotnet test MQArchLab.slnx --no-build
```

Then run the selected problem-frame compliance gate, JSON/link validators, database failure-injection tests, and broker profile gates. Record each result as passed, failed, blocked-by-environment, not-applicable, or owner-deferred. Only passed, or an explicitly policy-accepted owner deferral, can satisfy a required gate.

## Fresh-Context Review

A reviewer that did not participate in implementation must be able to answer from durable artifacts alone:

- What are the bounded contexts and ownership boundaries?
- Which public APIs/messages/schemas must remain compatible?
- What are the aggregate invariants and application failure semantics?
- Where are atomicity, idempotency, concurrency, retry, and ordering enforced?
- Which current quirks are intentionally not copied?
- What exact evidence proves acceptance?

Any answer that requires original source or hidden conversation means reconstruction readiness has failed.

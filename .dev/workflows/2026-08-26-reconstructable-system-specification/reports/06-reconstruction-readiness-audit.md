# RECON-006 Reconstruction Readiness Audit

## Verdict

`CONDITIONAL - the specification baseline and provisional source-outbox design are implemented; do not delete product source yet.`

The durable artifact set can start two source-independent LUNA-class reconstructions without this conversation. It is not proven sufficient to finish either run at accepted quality because the selected compliance gate is 89%, the opted-in PostgreSQL/Kafka evidence and the two clean-room reconstructions have not run, and the owner has not yet accepted the concrete transaction-port design.

## Durable Coverage

| Dimension | Result | Evidence |
| --- | --- | --- |
| Requirement identity and status vocabulary | covered | `.dev/requirement/reconstructable-system-baseline.md` |
| 22-product-project / 5-current-test-project topology | covered | `project-manifest.json` |
| DDD / Clean Architecture / Hexagonal boundaries | covered | `system-blueprint.md` |
| 3 bounded contexts, 3 aggregates, 16 use cases | covered | domain specs and coverage matrix |
| 15 HTTP endpoints | covered | `http-api-contracts.json` and adapter specs |
| Kafka canonical transport and partition ordering | covered as decision and adapter contract | ADR-003, `message-contracts.json`, `mq-topology.md` |
| Producer-owned Published Language | covered as normative ownership | `context-map.md`, `message-contracts.json` |
| Inventory reservation source outbox | covered in code, SQL, specs, and broker-free tests | ADR-004, `persistence-contracts.json`, Inventory implementation/tests |
| RabbitMQ deferred compatibility profile | bounded, runtime parity unproven | ADR-002, ADR-003, `runtime-contracts.json` |
| Correct Inventory increase/return event names | covered in code, JSON, and tests | event contracts and `InventoryIntegrationEventContractTests.cs` |
| 6 hosts, profiles, containers, observability | covered as design | `runtime-contracts.json` |
| Two source-free LUNA-class reconstruction proofs | not run | `.dev/specs/tests/e2e/reconstruction-acceptance.test-spec.md` |

## Concrete Provisional Architecture

```text
ReserveInventoryUseCase
  -> IInventoryReservationTransactionFactory.BeginAsync
  -> IInventoryReservationTransaction.ReserveAsync
  -> use case creates ProductStockDecreasedIntegrationEvent
  -> IInventoryReservationTransaction.StageAsync
  -> one PostgreSQL commit: stock + terminal outcome + InventoryIntegrationOutbox
  -> InventoryIntegrationOutboxRelay
  -> IIntegrationEventPublisher / Wolverine / Kafka
```

This design deliberately keeps event meaning in Application and persistence/relay mechanics in Infrastructure. The user may revise the transaction-port shape after inspecting the implementation; that review is a design gate, not evidence that the provisional implementation failed.

## Resolved And Deferred Decisions

- Resolved: Kafka is canonical; Inventory ordering uses normalized `ProductId` as partition key.
- Resolved: the producer owns integration-event meaning and schema; consumers own reactions, projections, idempotency, retry, and dead-letter handling.
- Resolved provisionally: ReserveInventory uses a transactional source outbox.
- Resolved: increase/return quantity properties use `IncreasedQuantity` and `ReturnedQuantity` with no legacy alias.
- Resolved provisionally: source deletion requires two independent clean-room LUNA-class reconstructions.
- Deferred: RabbitMQ fanout/queue topology or dual deployment, outbox retention, adoption by other Inventory commands, and final owner acceptance of the transaction-port design.

## Non-Passing Gates

- ReserveInventory spec compliance: 89%, `NOT COMPLIANT`; see report 05.
- Real PostgreSQL concurrency/outbox atomicity and failure injection: blocked because Docker Desktop is not running.
- Kafka runtime ordering and replay evidence for the new relay: not run against a live broker.
- RabbitMQ compatibility runtime: deferred and not part of the canonical acceptance path.
- Two independent LUNA-class reconstructions from a source-free disposable copy: not run.

## Deletion Gate

Source removal is permitted only as a separately authorized operation in disposable copies after all of these are true:

1. selected problem frames reach 100% compliance;
2. every required `gap` in `coverage-matrix.md` is passed or explicitly owner-resolved;
3. two independent LUNA-class agents reconstruct from documented inputs without `src/`, `tests/`, `.git/`, `bin/`, `obj/`, code graph, or conversation history;
4. each reconstruction uses isolated output and passes restore/build/default tests plus required PostgreSQL and Kafka gates;
5. a reviewer compares externally observable behavior and architecture constraints without requiring identical internal code;
6. the owner separately authorizes any source deletion.

Until then, retain current source and tests as protected comparison evidence. This audit authorizes no deletion, push, PR, merge, Issue closure, release, or publication.

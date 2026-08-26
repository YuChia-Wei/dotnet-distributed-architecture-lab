# RECON-006 Reconstruction Readiness Audit

## Verdict

`CONDITIONAL — documentation baseline established; do not delete the current product source yet.`

The durable artifact set is now sufficient to start a source-independent reconstruction without relying on this conversation. It is not yet proven sufficient to finish one at accepted quality because the selected compliance gate is 68%, the destructive-copy LUNA exercise has not run, and several owner/environment decisions remain open.

## Durable Coverage

| Dimension | Result | Evidence |
| --- | --- | --- |
| Requirement identity and status vocabulary | covered | `.dev/requirement/reconstructable-system-baseline.md` |
| 22-product-project / 4-current-test-project topology | covered | `project-manifest.json` |
| DDD / Clean Architecture / Hexagonal boundaries | covered | `system-blueprint.md` |
| 3 bounded contexts, 3 aggregates, 16 use cases | covered | domain specs and coverage matrix |
| 15 HTTP endpoints | covered | `http-api-contracts.json` and adapter specs |
| Published Language and MQ routes | covered with owner/environment gaps | `message-contracts.json` |
| Products/Orders/Inventory durability | covered as design | `persistence-contracts.json` |
| 6 hosts, profiles, containers, observability | covered as design | `runtime-contracts.json` |
| Critical cross-context behavior oracle | covered as frame/design | PlaceOrder and ReserveInventory CBFs plus test specs |
| Fresh-source deletion reconstruction proof | not run | `.dev/specs/tests/e2e/reconstruction-acceptance.test-spec.md` |

## Source-Independence Walk

A future agent can discover the authority order, read sequence, project graph, build order, aggregate rules, use-case inputs/outputs, API/message/persistence/runtime contracts, and acceptance procedure from `.dev/` alone. The reconstruction documents do not require code-graph access, an archived conversation, or generated caches.

The following facts still require an explicit decision or executable proof rather than source reading:

1. RabbitMQ physical topology and trusted runtime parity.
2. Product integration-event producer ownership.
3. Business ownership for subscribed consumer events.
4. Migration strategy for the misleading `DecreasedQuantity` property on increase/return contracts.
5. Whether Inventory success publication gains a transactional outbox in the reconstructed target.

## Non-Passing Gates

- ReserveInventory spec compliance: 68%, `NOT COMPLIANT`.
- Focused current test execution: interrupted during restore; not passing evidence.
- Real PostgreSQL reservation concurrency and Orders source-transaction failure injection: not proven.
- RabbitMQ runtime: blocked until a trusted environment run.
- Fresh LUNA-class reconstruction in a disposable source-free clone: not run.

## Deletion Gate

Source removal is permitted only in a disposable copy after all of these are true:

1. selected problem frames reach 100% compliance;
2. every `gap` in `coverage-matrix.md` is passed or explicitly owner-resolved;
3. a fresh LUNA-class agent reconstructs the repository from the documented entrypoint;
4. the reconstructed result passes restore/build/test, database durability, Kafka, and selected RabbitMQ gates;
5. a reviewer confirms no hidden source or conversation dependency.

Until then, retain the current source as protected comparison evidence. This audit does not authorize deletion, push, PR, merge, Issue closure, or publication.

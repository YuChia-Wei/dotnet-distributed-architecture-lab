# RECON-009 Spec Compliance Report

## Selection

- Problem frame: `.dev/problem-frames/inventory/cbf/reserve-inventory/`
- Aggregate / controlled domain: `InventoryItem` reservation and producer-owned source outbox
- Effective packet: `PACKET-D30CE87BD1F49C6BF04E18E179DEFFB9152CC2FD464D0A4E1B3D6B8841928A72`
- Route: `compliance-validation / direct / dotnet-backend / problem-frame-and-dotnet`
- Target-state digest: `ec489634d9af8e62468d5f61aff1eef8924fde9ad00111642ab3904eea31bb30`
- Freshness: `verified`
- Gate: every category must be 100%; no weighted score and no skipped external test can waive a missing item.

## Evidence Read

- All five CBF files under the selected frame.
- `ReserveInventoryUseCase`, both reservation outbox adapters, ordinary stock outbox adapter, `InventoryIntegrationOutboxRelay`, and the Inventory integration-event publisher.
- Inventory use-case, idempotency, contract, relay, retention, and default-skipped PostgreSQL tests.
- ReserveInventory and ordinary stock production/test specifications plus the Inventory outbox SQL migration.
- Best-effort helper `.ai/scripts/check-spec-compliance.sh` completed with no listed mapper, projection, or DTO omissions. That helper result does not replace the manual 100% frame checklist.

## Compliance Matrix

The percentage is a transparent checklist inventory, not a waiver. The unchanged 82-item ReserveInventory checklist continues to cover atomic source-outbox persistence, stable relay identity, and failure behavior. Current passing evidence covers `73 / 82 = 89.0%`, reported as 89%.

| Category | Covered | Total | Rate | Status |
| --- | ---: | ---: | ---: | --- |
| Use-case input fields | 3 | 3 | 100% | pass |
| Service preconditions | 3 | 3 | 100% | pass |
| Aggregate/transaction behavior signature | 1 | 1 | 100% | pass |
| Integration-event attributes | 4 | 4 | 100% | pass |
| Error-handling policies | 10 | 10 | 100% | pass |
| Constraints | 4 | 6 | 67% | fail: real-store non-negative stock and atomic rollback proof pending |
| Frame concerns FC1-FC6 | 5 | 6 | 83% | fail: FC3 real-store execution pending |
| Acceptance scenarios | 8 | 9 | 89% | fail: SC7 is default-skipped |
| Then-condition assertions | 19 | 22 | 86% | fail: SC7 has no passing runtime evidence |
| PRE/POST/INV contract semantics | 7 | 9 | 78% | fail: PostgreSQL POST1/INV1 proof pending |
| GWT semantic mapping | 9 | 9 | 100% | pass |
| **Overall inventory** | **73** | **82** | **89%** | **fail** |

## Missing Items

1. `SC7`, `FC3`, `POST1`, and `INV1` still require an opted-in real PostgreSQL run proving concurrent reservations serialize, stock never becomes negative, both terminal outcomes persist, and exactly one successful outbox row commits.
2. A real persistence failure-injection test is still needed to prove that failure while staging or committing rolls back stock, outcome, and outbox. Broker-free use-case tests cannot prove PostgreSQL rollback semantics.
3. The PostgreSQL tests are present and default-skipped by policy. Their skipped results are intentionally non-passing evidence.
4. The new ordinary-stock PostgreSQL checks prove the intended state/outbox and expected-stock contracts only when opted in; they were also skipped in the recorded default profile.

## Closed Remediation Items

- Application now exposes `IInventoryReservationOutbox` and `IInventoryStockOutbox`; transaction/UoW mechanics are private Infrastructure details.
- PostgreSQL stages stock, reservation outcome where applicable, and source-outbox intent in one local transaction.
- DecreaseStock, IncreaseStock, Restock, and successful ReserveInventory use producer-owned source outbox; InitProductStock does not invent an event.
- Matching reservation replay does not decrement stock or add a second outbox row; conflicting identity does not stage a success event.
- Relay retries preserve `MessageId`, partition key, and `OccurredOn`; successful relay retains publication evidence.
- Five consecutive publication failures park the row and a later relay pass does not republish it.
- Relay supports decreased, increased, and returned Inventory event types.
- Retention defaults to `RetainAll`; `PublishedForDays` requires a positive day count and targets only published rows.
- External-service tests remain opt-in; ordinary default tests require no Kafka, RabbitMQ, or PostgreSQL service.
- Kafka plus RabbitMQ dual broadcast is documented only as a target direction because the current row has no independent destination completion state.

## Test Execution Evidence

```text
dotnet build tests/InventoryControl.Tests/InventoryControl.Tests.csproj --no-restore --nologo --verbosity minimal -m:1 /nodeReuse:false /p:UseSharedCompilation=false
dotnet test tests/InventoryControl.Tests/InventoryControl.Tests.csproj --no-build --no-restore --nologo --verbosity minimal -m:1 /nodeReuse:false
dotnet test MQArchLab.slnx --no-build --no-restore --nologo --verbosity minimal -m:1 /nodeReuse:false
bash ./.ai/scripts/check-spec-compliance.sh .dev/specs/domains/inventory-item/usecase/reserve-inventory.json RECON-009
```

- Inventory build: passed, 0 warnings, 0 errors.
- Inventory default profile: 30 passed, 3 skipped, 0 failed.
- Full solution default profile: 66 passed, 3 skipped, 0 failed.
- Best-effort component helper: passed, with no listed mapper/projection/DTO omissions.
- No opted-in PostgreSQL result exists in this checkpoint; all three external checks remain non-passing.

## Remediation Contract

To reach the unchanged 100% gate:

- start a compatible PostgreSQL instance with both Inventory migrations;
- set `RUN_EXTERNAL_INTEGRATION_TESTS=true` and `INVENTORY_TEST_POSTGRES_CONNECTION_STRING`;
- run the `ExternalIntegration` category and retain SC7/FC3/POST1/INV1 evidence;
- add and run a real rollback failure-injection check;
- rerun this same 82-item checklist without treating skipped checks as passed.

## Verdict

`NOT COMPLIANT - 89%; 100% gate not reached.` Broker-free implementation and tests pass, but real-store evidence is incomplete. Original source deletion remains prohibited for AI execution.

# RECON-008 Spec Compliance Report

## Selection

- Problem frame: `.dev/problem-frames/inventory/cbf/reserve-inventory/`
- Aggregate / controlled domain: `InventoryItem` reservation transaction and source outbox
- Effective packet: `PACKET-D30CE87BD1F49C6BF04E18E179DEFFB9152CC2FD464D0A4E1B3D6B8841928A72`
- Route: `compliance-validation / direct / dotnet-backend / problem-frame-and-dotnet`
- Freshness: `verified`
- Gate: every category must be 100%; no weighted score can waive a missing item.

## Evidence Read

- All five CBF files under the selected frame.
- `ReserveInventoryUseCase`, both reservation transaction adapters, `InventoryIntegrationOutboxRelay`, and the Inventory integration-event publisher.
- Inventory use-case, idempotency, contract, relay, and opted-in PostgreSQL tests.
- ReserveInventory production/test specifications and the Inventory outbox SQL migration.

## Compliance Matrix

The percentage is a transparent checklist inventory, not a waiver. RECON-008 expands the contract from 66 to 82 items to cover atomic source-outbox persistence, stable relay identity, and failure behavior. Current evidence covers `73 / 82 = 89.0%`, reported as 89%.

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

1. `SC7`, `FC3`, `POST1`, and `INV1` need one opted-in real PostgreSQL run proving that concurrent reservations serialize, stock never becomes negative, both outcomes persist, and exactly one successful outbox row commits.
2. A real persistence failure-injection test is still needed to prove that failure while staging or committing rolls back stock, outcome, and outbox. The broker-free use-case test proves that `CommitAsync` is not called; it cannot prove PostgreSQL rollback semantics.
3. The PostgreSQL test is present and default-skipped by policy. A skipped result is intentionally not passing compliance evidence.

## Closed Remediation Items

- The application now owns one explicit reservation transaction and creates the producer-owned integration event before commit.
- PostgreSQL stages stock, terminal outcome, and the source-outbox row in one local transaction.
- Matching replay does not decrement stock or add a second outbox row; conflicting identity does not stage a success event.
- Relay retries preserve `MessageId`, partition key, and `OccurredOn`; successful relay retains publication evidence.
- Five consecutive publication failures park the row and a later relay pass does not republish it.
- Wolverine publication receives the stable message identity and normalized product partition key.
- Invalid input, cancellation, business failure, transient store failure, and staging failure are distinguished.
- Correct `IncreasedQuantity` and `ReturnedQuantity` JSON contracts are executable and the erroneous names are absent.
- External-service tests remain opt-in; ordinary default tests require no Kafka, RabbitMQ, or PostgreSQL service.

## Test Execution Evidence

```text
dotnet build tests/InventoryControl.Tests/InventoryControl.Tests.csproj --no-restore --nologo --verbosity minimal -m:1 /nodeReuse:false /p:UseSharedCompilation=false
dotnet test tests/InventoryControl.Tests/InventoryControl.Tests.csproj --no-build --no-restore --nologo --verbosity minimal -m:1 /nodeReuse:false
dotnet test MQArchLab.slnx --no-restore --nologo --verbosity minimal -m:1 /nodeReuse:false /p:UseSharedCompilation=false
```

- Inventory build: passed, 0 warnings, 0 errors.
- Inventory default profile: 27 passed, 1 skipped, 0 failed.
- Full solution default profile: 63 passed, 1 skipped, 0 failed.
- Docker Desktop was not running, so no opted-in PostgreSQL result exists.

## Remediation Contract

To reach the unchanged 100% gate:

- start a compatible PostgreSQL instance with both Inventory migrations;
- set `RUN_EXTERNAL_INTEGRATION_TESTS=true` and `INVENTORY_TEST_POSTGRES_CONNECTION_STRING`;
- run the `ExternalIntegration` category and retain SC7/FC3/POST1/INV1 evidence;
- add a real rollback failure-injection check;
- rerun this same 82-item checklist without treating skipped checks as passed.

## Verdict

`NOT COMPLIANT - 89%; 100% gate not reached.` Broker-free implementation and tests pass, but the strengthened real-store evidence is incomplete. Source deletion remains prohibited.

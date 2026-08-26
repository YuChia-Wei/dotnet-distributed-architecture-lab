# RECON-005 Spec Compliance Report

## Selection

- Problem frame: `.dev/problem-frames/inventory/cbf/reserve-inventory/`
- Aggregate / controlled domain: `InventoryItem` reservation transaction
- Effective packet: `PACKET-D30CE87BD1F49C6BF04E18E179DEFFB9152CC2FD464D0A4E1B3D6B8841928A72`
- Route: `compliance-validation / direct / dotnet-backend / problem-frame-and-dotnet`
- Freshness: `verified`
- Gate: every category must be 100%; no weighted score can waive a missing item.

## Evidence Read

- All five CBF files under the selected frame.
- `ReserveInventoryUseCase`, `PostgresInventoryReservationRepository`, `InMemoryInventoryReservationRepository`, and the request-contract handler.
- `InventoryReservationIdempotencyTests.cs` and reusable `InventoryStockUseCaseTests.cs` contract assertions.
- The new ReserveInventory test specification.

## Compliance Matrix

The overall percentage is a transparent checklist inventory, not a waiver. After RECON-007 remediation, `62 / 66 = 94%`.

| Category | Covered | Total | Rate | Status |
| --- | ---: | ---: | ---: | --- |
| Use-case input fields | 3 | 3 | 100% | pass |
| Service preconditions | 3 | 3 | 100% | pass |
| Aggregate/repository behavior signature | 1 | 1 | 100% | pass |
| Integration-event attributes | 4 | 4 | 100% | pass through shared stock-event contract test |
| Error-handling policies | 9 | 9 | 100% | pass |
| Constraints | 4 | 5 | 80% | fail: real store execution pending |
| Frame concerns FC1–FC6 | 5 | 6 | 83% | fail: FC3 execution pending |
| Acceptance scenarios | 6 | 6 | 100% | pass |
| Then-condition assertions | 15 | 15 | 100% | pass |
| PRE/POST/INV contract semantics | 6 | 8 | 75% | fail: PostgreSQL POST1/INV1 proof pending |
| GWT semantic mapping | 6 | 6 | 100% | pass |
| **Overall inventory** | **62** | **66** | **94%** | **fail** |

## Missing Items

1. `FC3`, `POST1`, and `INV1` still require one opted-in real PostgreSQL run proving concurrent reservations serialize through `FOR UPDATE`, never produce negative stock, and atomically persist both outcomes with stock.
2. The required test now exists and is default-skipped by policy. A skipped result is intentionally not counted as passing compliance evidence.

## Closed Remediation Items

- `PRE1`–`PRE3` / `SC5`: exact invalid-input reasons and zero repository/publisher interactions are covered.
- `SC3`: operation identity conflict now asserts no success publication.
- `FC6`: transient durable-store failure and publish-after-commit failure/replay are distinguished from business rejection.
- `InventoryIsNotEnough` is exercised through `ReserveInventoryUseCase` with no publication.
- Inventory behavior is owned by `tests/InventoryControl.Tests` rather than the Orders test project.
- The external-integration contract is documented in `tests/README.md`; ordinary configuration and in-memory transport tests remain in the default profile.

## Test Execution Evidence

A prior focused command in the original mixed test project was interrupted. RECON-007 used single-node MSBuild/test execution to avoid the host's uncontrolled process fan-out:

```text
dotnet build tests/InventoryControl.Tests/InventoryControl.Tests.csproj --no-restore --nologo --verbosity minimal -m:1 /nodeReuse:false /p:UseSharedCompilation=false
dotnet test tests/InventoryControl.Tests/InventoryControl.Tests.csproj --no-build --no-restore --nologo --verbosity minimal -m:1 /nodeReuse:false
dotnet test tests/SaleOrders.Tests/SaleOrders.Tests.csproj --no-restore --nologo --verbosity minimal -m:1 /nodeReuse:false /p:UseSharedCompilation=false
```

- Inventory build: passed, 0 errors; one pre-existing nullable warning in `DomainEntity.Id`.
- Inventory default profile: 19 passed, 1 skipped (the PostgreSQL external integration test), 0 failed.
- Orders regression profile: 11 passed, 0 skipped, 0 failed; three pre-existing nullable warnings in `Order.ProductName`.
- Docker Desktop was not running, so no opted-in PostgreSQL result exists.

## Remediation Contract

The implementation slice is complete. The remaining closeout action is environment-dependent execution:

- start a compatible PostgreSQL instance with the Inventory schema;
- set `RUN_EXTERNAL_INTEGRATION_TESTS=true` and `INVENTORY_TEST_POSTGRES_CONNECTION_STRING`;
- run the `ExternalIntegration` category;
- retain the result as FC3/POST1/INV1 evidence and rerun this unchanged checklist.

## Verdict

`NOT COMPLIANT — 94%; 100% gate not reached.` Static implementation and broker-free execution gaps are closed, but the real PostgreSQL concurrency proof is `blocked-by-environment`, not passed.

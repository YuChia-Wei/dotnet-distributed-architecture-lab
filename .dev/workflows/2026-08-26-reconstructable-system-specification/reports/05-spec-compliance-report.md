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

The overall percentage is a transparent checklist inventory, not a waiver. `45 / 66 = 68%`.

| Category | Covered | Total | Rate | Status |
| --- | ---: | ---: | ---: | --- |
| Use-case input fields | 3 | 3 | 100% | pass |
| Service preconditions | 0 | 3 | 0% | fail |
| Aggregate/repository behavior signature | 1 | 1 | 100% | pass |
| Integration-event attributes | 4 | 4 | 100% | pass through shared stock-event contract test |
| Error-handling policies | 3 | 9 | 33% | fail |
| Constraints | 3 | 5 | 60% | fail |
| Frame concerns FC1–FC6 | 4 | 6 | 67% | fail |
| Acceptance scenarios | 5 | 6 | 83% | fail |
| Then-condition assertions | 12 | 15 | 80% | fail |
| PRE/POST/INV contract semantics | 5 | 8 | 63% | fail |
| GWT semantic mapping | 5 | 6 | 83% | fail |
| **Overall inventory** | **45** | **66** | **68%** | **fail** |

## Missing Items

1. `PRE1`–`PRE3` / `SC5`: no executable tests prove empty operation id, empty product id, and non-positive quantity return their exact reasons without repository or publisher calls.
2. `FC3`, `POST1`, and `INV1`: no real PostgreSQL test proves concurrent reservations serialize through `FOR UPDATE`, never produce negative stock, and atomically persist operation outcome with stock.
3. `SC3`: the conflict test proves result and stock but does not assert that no success event is published.
4. `FC6`: no test distinguishes `InventoryReservationTransientException` and publisher failure from business rejection, including replay after publication failure.
5. Failure coverage does not directly exercise `InventoryIsNotEnough` through the reservation repository/use case.
6. Inventory behavior remains hosted in `SaleOrders.Tests`; the required independent Inventory test surface does not exist.

## Test Execution Evidence

A focused command was attempted:

```text
dotnet test tests/SaleOrders.Tests/SaleOrders.Tests.csproj --filter "FullyQualifiedName~InventoryReservationIdempotencyTests|FullyQualifiedName~InventoryStockUseCaseTests" --nologo
```

The command remained in restore with no further output and spawned a large restore/build process fan-out. It was stopped after bounded observation. Outcome: `interrupted`, not passing. No product or test files were modified.

## Remediation Contract

The missing executable work belongs to a separately authorized test-implementation slice:

- create an Inventory-owned test project;
- implement SC5 validation and no-interaction assertions;
- add PostgreSQL transaction/concurrency fixtures for FC3;
- add no-publication assertions for conflict/business failures;
- add transient store and publisher failure/replay tests;
- rerun this same frame without relaxing categories.

## Verdict

`NOT COMPLIANT — 100% gate not reached.` The problem frame and test design are validator-ready, but the repository is not yet safe to treat as executable reconstruction proof.

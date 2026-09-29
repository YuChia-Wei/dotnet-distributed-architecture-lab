# Procurement formal-test specifications

Bound source: `179b3e12bb1e5f1c67cee3158ccd414bd9a8b6a5`, inspected 2026-09-29. These are formal-test specifications authored from the [current production contracts](../../domains/procurement/README.md) and [original P/R/S/M/U/V scenario inventory](../../../workflows/2026-09-26-procurement-supplier-lab/test-specification.md). Existing IDs are retained. `PS-V*` names identify newly documented verification targets only; they do not imply new approved product behavior or newly implemented tests.

## Formal specification map

- [Aggregate invariants and receipt state](aggregate/purchase-order.test-spec.md).
- [Six application operations and failure semantics](use-cases/purchase-operations.test-spec.md).
- [PostgreSQL and supplier HTTP adapters](integration/procurement-adapters.test-spec.md).
- [GoodsReceived and Inventory receipt processing](../cross-domain/procurement-inventory-receipt.test-spec.md).

## Presence versus execution

All entries below are **source/test presence observations**, not executions at this revision. `partial` means the named file supports part of the scenario; it does not measure numerical coverage. No .NET, PostgreSQL, HTTP proxy, browser or Kafka test was run for this documentation supplement. [Earlier acceptance evidence](../../../workflows/2026-09-26-procurement-supplier-lab/acceptance-report.md) remains bound to its earlier target/date.

| Original IDs | Existing evidence locations | Coverage boundary |
| --- | --- | --- |
| P01, P02, P03, P04, P05, P06, P07 | [PurchaseScenarios.cs](../../../../tests/Procurement.Tests/PurchaseScenarios.cs), [SupplierGatewayScenarios.cs](../../../../tests/Procurement.Tests/SupplierGatewayScenarios.cs) | Unit/application fake store or stub HTTP; P04 lookup/unknown handling is not actual delayed-after-commit HTTP |
| P02, P03 | [PurchasePostgresScenarios.cs](../../../../tests/Procurement.Tests/PurchasePostgresScenarios.cs) | Opt-in PostgreSQL concurrent create/replay and changed identity; not one-supplier-order proof |
| R01, R03, R04 | [ReceiptScenarios.cs](../../../../tests/Procurement.Tests/ReceiptScenarios.cs) | Local aggregate/application behavior; not eventual Inventory observation |
| R02, R03, R04, R05, R06 | [ReceiptPostgresScenarios.cs](../../../../tests/Procurement.Tests/ReceiptPostgresScenarios.cs) | Opt-in local transactions, receipt race, replay after outbox removal, precision and snapshot consistency |
| R03, R04, R05, R07 | [Inventory store tests](../../../../tests/InventoryControl.Tests/PostgresInventoryGoodsReceiptStoreTests.cs) | Real PostgreSQL opt-in; consumer/use-case mapping has separate unit tests |
| P02, P03, P04, P07, S01, M01–M06 | [test_contracts.py](../../../../scripts/procurement-lab/test_contracts.py) | Actual HTTP script when services run; engine mode/provenance assertions are not established by stub tests |
| S01 (partial) | [SupplierSandboxTests.cs](../../../../tests/SupplierSandbox.Tests/SupplierSandboxTests.cs) | Real Sandbox PostgreSQL key replay/conflict and concurrency; application/storage tests do not prove an HTTP 409 response |
| P04 | [test_supplemental_contracts.py](../../../../scripts/procurement-lab/test_supplemental_contracts.py) | Actual delayed supplier submission plus no-stock-before-receipt assertion |
| R01, R03 | [Test-Flow.ps1](../../../../scripts/procurement-lab/Test-Flow.ps1) | Actual purchase/receipts/Inventory observation using initialized product |
| R08 | [test_broker_recovery.py](../../../../scripts/procurement-lab/test_broker_recovery.py) | Explicitly interrupts lab Kafka and checks recovery; local outbox test alone does not cover it |
| U01–U03 | Original lab browser evidence and [demo guide](../../../guides/external-api-testing/demo-guide.md) | Tool UI belongs to supplier lab, not Procurement domain ownership; no current browser run |
| V01, V02 | Original lab verification/model-review records | Historical quality criteria; this document is not a new regression run or model benchmark |

## Execution prerequisites and isolation

Procurement uses plain xUnit v3 with recognizable Given/When/Then steps, NSubstitute where the project selects it, and deterministic port/HTTP fakes for unit tests. No BDDfy or `.feature` runner is introduced.

Existing commands, for a later authorized verification run:

```powershell
dotnet test tests/Procurement.Tests/Procurement.Tests.csproj
dotnet test tests/InventoryControl.Tests/InventoryControl.Tests.csproj
```

PostgreSQL scenarios require `RUN_EXTERNAL_INTEGRATION_TESTS=true` **and** `PROCUREMENT_TEST_POSTGRES_CONNECTION_STRING` or `INVENTORY_TEST_POSTGRES_CONNECTION_STRING` respectively. Missing opt-in yields skipped external tests, not passing database evidence. Provision schema from checked-in additive migrations and use dedicated test identities. Preserve shared rows, volumes and containers; clean only known test data. HTTP scripts change shared mock modes and Sandbox delay, so isolate the run and restore agreed settings after retaining evidence. Quote GET lacks clientRequestId; isolate SKU/time observations instead of inferring causality from a shared request count. Broker recovery needs explicit environment coordination and initialized Inventory; see the operation guide before execution.

Sandbox PostgreSQL tests have a separate prerequisite: `SUPPLIER_TEST_POSTGRES_CONNECTION_STRING`. [SupplierSandboxTests](../../../../tests/SupplierSandbox.Tests/SupplierSandboxTests.cs) checks that variable and skips when absent; it does not use the Procurement/Inventory `RUN_EXTERNAL_INTEGRATION_TESTS` gate. Its project can be selected with `dotnet test tests/SupplierSandbox.Tests/SupplierSandbox.Tests.csproj`. This command was not run for this supplement.

## Open verification scope

PS-V01–PS-V06 below add explicit acceptance descriptions for recovered subtleties; no full executable coverage is claimed for them. Document checks cannot establish HTTP status mapping, cancellation persistence, SQL race behavior, or delivery durability. A complete future compliance assessment must bind each applicable assertion to actual revision/environment/output, including skips and failures, rather than treating this matrix or old AC labels as a pass.

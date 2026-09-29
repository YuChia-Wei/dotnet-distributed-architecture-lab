# Procurement persistence and supplier adapter formal-test specification

Type: formal-test. Bound source `179b3e12bb1e5f1c67cee3158ccd414bd9a8b6a5`; production [persistence/messaging](../../../domains/procurement/adapter/persistence-and-messaging.md) and [supplier gateway](../../../domains/procurement/adapter/supplier-gateway.md). AC01–AC03, BR01/BR04–BR06. [Run prerequisites and coverage ledger](../README.md).

## PostgreSQL scenarios

Use a real isolated PostgreSQL database with the tracked Procurement schema, unique test IDs, and the existing opt-in flags. Capture rows/results after committed transactions; do not substitute mocked connections or count calls as evidence of rollback.

| ID | Given | When | Then |
| --- | --- | --- | --- |
| P02 | Two callers, same client key/payload | Concurrent CreateOrGet/create | Exactly one purchase row and one local ID; all successful callers return same identity; this alone does not prove one external HTTP attempt |
| P03 | Existing client key | Change product/provider/quantity or another identity field through the use case | purchase_identity_conflict; original row unchanged and no supplier call for the conflicting request; HTTP 409 is a separate PS-V05 host assertion |
| R02, R06 | Accepted order with remaining quantity less than combined concurrent receipts | Race two receipts / attempt over-receipt | Sum never exceeds ordered quantity; failed attempt creates no durable receipt/outbox |
| R03 | Completed receipt, including after deleting only its test-owned outbox row | Replay matching receipt | Original receipt/time, no new event row; current order snapshot may include later receipts |
| R04 | Receipt ID already belongs to another purchase/product or quantity | Reuse ID | Identity conflict; no changed order/receipt/outbox |
| R05 | Two concurrent callers with same new receipt identity | Commit receipt | One receipt, one source outbox row, one aggregate received-quantity change; matching result stable; Inventory stock needs its own observation |
| PS-V06 | Concurrent receipt update and order/receipt read | Read snapshot | Order received total agrees with receipts in the same repeatable-read snapshot |
| PS-V06 | First receipt obtains an application-generated UTC timestamp | Commit then read/replay | Application output, persisted receipt and serialized event/replay ReceivedAt agree at millisecond precision; a controlled sub-millisecond input and actual HTTP serialization need additional tests |

Existing [PurchasePostgresScenarios](../../../../../tests/Procurement.Tests/PurchasePostgresScenarios.cs) and [ReceiptPostgresScenarios](../../../../../tests/Procurement.Tests/ReceiptPostgresScenarios.cs) support the PostgreSQL/application assertions above. They do not exercise actual HTTP status/body serialization, every possible identity-field variant or a controlled source clock. One source outbox row does not prove broker publish/consumer completion. Inventory rollback and actual R08 are in the [cross-context specification](../../cross-domain/procurement-inventory-receipt.test-spec.md).

## Supplier boundary scenarios

| ID | Level / Given | When | Then |
| --- | --- | --- | --- |
| P05 | Stubbed HttpMessageHandler returns malformed/null/identity-mismatched body, unknown status, whitespace origin, or invalid supplier ID | Submit/lookup | supplier_invalid_response; never accept mismatched identity |
| P05 | Stubbed HTTP 408/504, 5xx, network failure or caller cancellation | Quote/submit/lookup | Timeout/unavailable/cancellation mapping as specified; cancellation source distinguished |
| M04 (partial) | Stubbed Microcks base URL includes API/version path prefix | Call gateway | Relative supplier route preserves prefix; this is only path construction evidence |
| S01 | Real Sandbox PostgreSQL and distinct test key | Repeat/race same payload then change it | One logical supplier order and stable ID; changed payload 409 |
| P04 | Real Sandbox delayed after committed POST, timeout shorter than delay | Create then lookup/reconcile | One persisted supplier order; local unknown can recover through original key; stock remains unchanged |
| M01–M06 | Actual native engines with known fixture, selected mock/proxy/hybrid mode, recorded baseline | Issue matching/unmatched known-operation requests through each provider | Read native effective configuration, response origin and Sandbox request observations; mock adds no upstream request, proxy does; unknown Microcks paths have no blanket catch-all promise |

[SupplierGatewayScenarios](../../../../../tests/Procurement.Tests/SupplierGatewayScenarios.cs) currently covers Submit 5xx, malformed JSON, status/identity mismatch, network/deadline, caller cancellation, and one successful Quote with the Microcks prefix. The other proposed stub conditions above (null/whitespace origin/invalid supplier ID, lookup validation, explicit HTTP 408/504 and Quote/Lookup transport variants) remain verification targets without dedicated test presence established here. [SupplierSandboxTests](../../../../../tests/SupplierSandbox.Tests/SupplierSandboxTests.cs) supports the real Sandbox database identity assertions but does not exercise HTTP 409. [test_contracts.py](../../../../../scripts/procurement-lab/test_contracts.py) and [test_supplemental_contracts.py](../../../../../scripts/procurement-lab/test_supplemental_contracts.py) support actual HTTP cases. Exact origin/header provenance is not enforced by gateway, so an arbitrary nonblank origin is not authenticity proof. Record POST clientRequestId or isolate quote GET SKU/time observations. Preserve native request logs before resets; reset may clear them.

No test in this file was executed as part of authoring. Dedicated HTTP controller mapping, all price boundary values, and every recovery branch are not asserted fully covered merely because a P/M ID occurs in a test file. Bind future results to command, source revision, environment and individual assertions.

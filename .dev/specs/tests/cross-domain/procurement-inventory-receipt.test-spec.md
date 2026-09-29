# Procurement to Inventory receipt formal-test specification

Type: formal-test. Source `179b3e12bb1e5f1c67cee3158ccd414bd9a8b6a5`, inspected 2026-09-29. Requirements US03–US04 / AC02 / BR03–BR05, BR07. Production [receipt use case](../../domains/procurement/usecase/receive-goods.json) and [message/persistence contract](../../domains/procurement/adapter/persistence-and-messaging.md). Original R01–R08 IDs remain unchanged. Execution status: **not run for this documentation supplement**.

## Owners and dependencies

Procurement commits receipt and source outbox. Its WebApi relay hands GoodsReceived to durable Wolverine/Kafka. Inventory Consumer delegates to its receipt use case; Inventory owns the ledger, stock and outgoing stock event. This is two local transactions with asynchronous delivery, not a distributed SQL transaction.

Inventory production sources: [handler](../../../../src/Inventory/Presentation/InventoryControl.Consumer/Messaging/GoodsReceivedHandler.cs), [use case and capabilities](../../../../src/Inventory/DomainCore/InventoryControl.Applications/Receipts/InventoryGoodsReceipt.cs), [Postgres store](../../../../src/Inventory/DomainCore/InventoryControl.Infrastructure/Applications/Repositories/PostgresInventoryGoodsReceiptStore.cs).

## Scenarios and observable assertions

| ID | Level / Given | When | Then |
| --- | --- | --- | --- |
| R01 | E2E: existing initialized product, stock20, accepted quantity10 | Receive6 then4 under distinct ReceiptIds | Procurement partial then complete; eventual Inventory stock26 then30; acceptance alone never changes stock |
| R03 | Real PG: matching receipt already applied, possibly its outgoing outbox removed after completion | Redeliver same identity | Return original resulting stock; no new increment and no new stock outbox; do not invoke event factory on terminal replay |
| R04 | Real PG: same ReceiptId with changed PO, product or quantity | Redeliver | Conflict without partial mutation; handler propagates failure instead of acknowledging business success |
| R05 | Real PG: concurrent same receipt, or different receipts for one product | Apply concurrently | Same-key effect once; distinct receipts serialize correctly, no lost stock update |
| R07 | Real PG: missing Inventory row or forced outbox/staging failure | Apply; then retry when precondition/fault is corrected | Initial claim/stock/outbox rolls back; missing inventory is not silently initialized; valid retry succeeds once |
| R07 | Real PG: Int32 stock overflow | Apply receipt | Claim/stock/outbox remains unchanged; existing test does not prove a corrected-overflow retry |
| R08 | Actual Kafka lab: committed receipt while broker unavailable | Restore selected broker; wait for delivery, then replay matching HTTP receipt | Source/Wolverine durable intent survives, Inventory ledger/stock confirms receipt once after recovery and HTTP replay; no false pass from published_at alone |
| PS-V06 | Unit/contract: same ReceiptId/PO/product/quantity with different ReceivedAt | Map then apply | Timestamp remains message provenance, not an Inventory identity field; mapping contains only the four business identity fields |

R02/R06 over-receipt ownership remains Procurement and is specified in its [adapter tests](../procurement/integration/procurement-adapters.test-spec.md). Receipt replay does not imply global event ordering or exactly-once transport.

The R08 script does not explicitly inject a duplicate Kafka envelope or establish that broker redelivery occurred. A redelivery-specific live assertion requires injecting/observing the same GoodsReceived message identity again and reading the Inventory ledger/stock afterward. The PostgreSQL R03/R05 cases separately verify duplicate application-input handling.

## Existing test presence

- [GoodsReceivedHandlerTests](../../../../tests/InventoryControl.Tests/GoodsReceivedHandlerTests.cs): one mapping/use-case delegation and conflict propagation; unit boundary only.
- [ApplyGoodsReceiptUseCaseTests](../../../../tests/InventoryControl.Tests/ApplyGoodsReceiptUseCaseTests.cs): StockIncreased event and stable receipt-derived message identity; fake capability boundary.
- [PostgresInventoryGoodsReceiptStoreTests](../../../../tests/InventoryControl.Tests/PostgresInventoryGoodsReceiptStoreTests.cs): actual database replay/conflict/concurrency/rollback/overflow, opt-in only.
- [Test-Flow.ps1](../../../../scripts/procurement-lab/Test-Flow.ps1) and [broker recovery script](../../../../scripts/procurement-lab/test_broker_recovery.py): live cross-service checks when actually executed.

Use `RUN_EXTERNAL_INTEGRATION_TESTS=true` and `INVENTORY_TEST_POSTGRES_CONNECTION_STRING` for database scenarios; Procurement database tests additionally need its own connection variable. For E2E, provision both schemas, existing ProductId/Inventory and actual Kafka profile. Record command, revisions, before/after stock, receipt identity, source/Wolverine outbox states and Inventory ledger. Only operate on the expressly selected lab Compose project; preserve volumes and protected observability. Broker recovery intentionally stops Kafka and is not a routine document check.

The [historical lab acceptance report](../../../workflows/2026-09-26-procurement-supplier-lab/acceptance-report.md) has prior observations. Those runs are not re-labeled as passes at the bound revision. PS-V06's timestamp assertion is newly explicit; no dedicated executable test coverage or current compliance percentage is claimed.

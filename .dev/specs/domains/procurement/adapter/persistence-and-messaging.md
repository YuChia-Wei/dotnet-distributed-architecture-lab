# Procurement persistence and receipt messaging

Type: persistence/outbound-message adapter with an explicitly separate Inventory consumer boundary. Source revision `179b3e12bb1e5f1c67cee3158ccd414bd9a8b6a5`; requirements BR01/BR04/BR05/BR07, AC01/AC02. [Scope and authority](../README.md).

## Schema authority

Procurement uses its own PostgreSQL database through Dapper/Npgsql. [001-procurement.sql](../../../../../docker-compose/sql-script/procurement/001-procurement.sql) is additive `CREATE IF NOT EXISTS` schema authority; it is not a destructive reset or a complete upgrade mechanism for an incompatible existing schema.

| Table | Fields and constraints |
| --- | --- |
| procurement_purchase_orders | id UUID PK; client_request_id UUID unique; product_id UUID; supplier_sku varchar(64); quantity int >0; unit_price numeric(18,2) >=0; currency varchar(3) =TWD; provider varchar(16) in fixed profiles; state varchar(32); nullable supplier_order_id varchar(128); received_quantity int 0..quantity; version int; created_at/updated_at timestamptz |
| procurement_receipts | receipt_id UUID global PK; purchase_order_id UUID FK to order; product_id UUID; quantity int >0; received_at timestamptz; index on purchase_order_id |
| procurement_outbox | id UUID PK/FK to receipt; partition_key varchar(32); payload jsonb; attempts; next_attempt_at; locked_by UUID/locked_until; published_at; parked_at; last_error varchar(4000); created_at; pending index where published_at and parked_at are null |

Not-null requirements and defaults are in the SQL. There is no cross-database foreign key to Products/Inventory, and SQL state text has no enum CHECK. Domain validation and trusted hydration supply the state contract. No Procurement purge/retention or automatic parked-message replay API is defined here.

## Local transaction boundaries

Source: [PostgresPurchaseStore](../../../../../src/Procurement/DomainCore/Procurement.Infrastructure/PostgresPurchaseStore.cs); application capabilities are [defined here](../../../../../src/Procurement/DomainCore/Procurement.Applications/ProcurementOperations.cs).

| Capability | Atomicity, concurrency and replay |
| --- | --- |
| CreateOrGetAsync | INSERT ON CONFLICT(client_request_id) creates at most one local identity; subsequent repeatable-read load returns committed order/receipts. Application RequireIdentity detects conflicting payload before supplier POST. Supplier call occurs outside the local transaction. |
| Get/Recent reads | Repeatable-read projection of order and receipts avoids a mixed snapshot. Recent reads are bounded; no offset/cursor API. |
| ApplyOutcomeAsync / MarkUnknownAsync | Lock order FOR UPDATE, apply aggregate rule and persist conditionally. Concurrent settled outcome cannot be downgraded by a late failure. Version is not an HTTP optimistic-concurrency token. |
| Receipt CommitAsync | Lock order FOR UPDATE; check global receipt owner; execute local aggregate decision. First receipt commits order, receipt and outbox together. Exception rolls back all local changes. |
| Matching receipt replay | Return original receipt without staging another outbox, including after source outbox removal. Return current order snapshot; a previously published event is not recreated. |
| Conflicting receipt / over-receipt race | Same ReceiptId on another order or changed quantity conflicts; same-order row lock ensures cumulative receipt never exceeds ordered quantity. |

New receipt time uses `DateTimeOffset.FromUnixTimeMilliseconds(...)` to keep response, persisted fact, replay and event payload identical through PostgreSQL. Domain receipts have no external I/O. A committed purchase has no GoodsReceived until a physical receipt is committed.

## Producer-owned event and relay

`Lab.BoundedContextContracts.Procurement.IntegrationEvents.GoodsReceived` carries Guid ReceiptId, PurchaseOrderId, ProductId, positive Int32 Quantity, and DateTimeOffset ReceivedAt. See [contract source](../../../../../src/BC-Contracts/Lab.BoundedContextContracts.Procurement/IntegrationEvents/GoodsReceived.cs). ReceiptId is both source outbox identity and logical message identity; partition is ProductId in Guid `N` format. ReceiptId is not a new event ID on retry.

[ProcurementOutboxRelay](../../../../../src/Procurement/DomainCore/Procurement.Infrastructure/ProcurementOutboxRelay.cs) polls every 2 seconds. It claims up to 20 eligible rows with SKIP LOCKED, a 30-second lease and a fresh lock owner. Attempts increase on claim; failure delays are min(120, 2^min(attempts,7)) seconds, and attempt 8 parks the row. It preserves last error for diagnosis. Do not interpret a healthy API or a parked row as successful delivery.

The relay calls Wolverine PublishAsync with DeduplicationId=`ReceiptId:N`, PartitionKey=`ProductId:N`, and `lab-message-id`=`ReceiptId:D`. Under Kafka profile the host uses PostgreSQL durable Wolverine storage (`procurement_wolverine`) and topic `procurement.integration.events`. `published_at` is written after awaited durable Wolverine handoff; it does not prove Kafka or Inventory consumed the event. Publishing and source-row marking are separate, so a crash or lease expiry can duplicate handoff. Transport is at least once; there is no global ordering or exactly-once transport promise.

Program supports InMemory and Kafka profiles. Checked-in appsettings selects InMemory for local isolated hosting; Compose selects the integration configuration. Only Kafka-profile observations can establish real broker behavior. See [host composition](../../../../../src/Procurement/Presentation/Procurement.WebApi/Program.cs) and [Compose overlay](../../../../../docker-compose/docker-compose.procurement.yml).

## Inventory-owned receipt processing

Inventory Consumer maps GoodsReceived once to `ApplyGoodsReceiptInput(ReceiptId, PurchaseOrderId, ProductId, Quantity)` and delegates to its use case. ReceivedAt is provenance carried in the event; it is deliberately not part of Inventory dedup identity. Do not require conflict solely because a replay timestamp differs.

Inventory's separate local transaction claims ReceiptId, compares purchase/product/quantity on replay, locks existing InventoryItem, performs checked stock increase, records completion/result stock and stages `ProductStockIncreasedIntegrationEvent`. Matching terminal replay returns the original resulting stock and does not call the outbox factory or recreate removed outbox rows. Different purchase/product/quantity conflicts. Missing Inventory, overflow or staging failure rolls back the claim/stock/outbox so a later valid retry can succeed. A conflicting message is an error, not a successful business acknowledgement. Producer acceptance is not receipt consumption.

Source bindings:

- [GoodsReceivedHandler](../../../../../src/Inventory/Presentation/InventoryControl.Consumer/Messaging/GoodsReceivedHandler.cs).
- Inventory receipt use case/store and exact current test files are linked in the [cross-context test specification](../../../tests/cross-domain/procurement-inventory-receipt.test-spec.md).
- [Event catalog](../../../../operations/event-catalog.md), [MQ topology](../../../../operations/mq-topology.md), and [receipt sequence](../../../../guides/external-api-testing/sequences.md).

## Verification and limits

Real PostgreSQL tests are required for uniqueness, row locks, transaction rollback and coherent snapshots. Fake store or event construction cannot prove these properties. Broker recovery requires actual Kafka interruption and restoration in the explicitly selected lab project, with source outbox, Wolverine, Inventory ledger and stock observations. See [formal test index](../../../tests/procurement/README.md). This supplement performed document checks only and does not replace historical run evidence with a new pass.

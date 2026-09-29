# PurchaseOrder aggregate specification

Type: entity. Source-reconciled at `179b3e12bb1e5f1c67cee3158ccd414bd9a8b6a5` on 2026-09-29. Scope and authority: [Procurement entry](../README.md); requirement BR01–BR06. Implementation: [PurchaseOrder.cs](../../../../../src/Procurement/DomainCore/Procurement.Domains/PurchaseOrder.cs).

## Identity, ownership and structure

`PurchaseOrder` implements `IProcurementAggregateRoot`. Its local Id is a nonempty Guid; CreatePurchase uses `Guid.NewGuid()`. It is not event-sourced and does not derive from the shared domain-event aggregate base. `GoodsReceipt` is an immutable fact owned by this aggregate, not a new bounded context. ProductId and supplier order ID refer to external owners.

| Field | Type / invariant |
| --- | --- |
| Id | Guid, immutable local identity |
| Identity | Immutable `PurchaseIdentity` record; all seven fields participate in equality |
| Identity.ClientRequestId / ProductId | Nonempty Guid; client key globally unique in Procurement storage |
| Identity.SupplierSku | 1–64 ASCII letters, digits, hyphen or underscore; ordinal/case-sensitive string equality |
| Identity.Quantity | Positive Int32 |
| Identity.UnitPrice | Decimal, 0..9999999999999999.99 inclusive; rounding to two decimal places leaves the value unchanged |
| Identity.Currency / Provider | Exactly TWD / one of direct, wiremock, microcks; no case normalization |
| State | PendingSubmission, SubmissionUnknown, Accepted, Rejected, PartiallyReceived, Received |
| SupplierOrderId | Null before a known outcome; applying an outcome requires nonblank text <=128 characters |
| ReceivedQuantity | 0..Identity.Quantity; changes only on first receipt |
| Version | Starts at 0; increments on a new outcome, an unsettled MarkUnknown, or a new receipt |
| CreatedAt / UpdatedAt | DateTimeOffset; application supplies UTC; receipts use millisecond UTC precision |
| Receipts | Read-only view of owned GoodsReceipt(ReceiptId, PurchaseOrderId, ProductId, Quantity, ReceivedAt) |

Creation validates the identity before I/O. `invalid_identity`, `invalid_sku`, and `invalid_purchase` report the corresponding constraint failure. Restore hydrates stored fields directly; it is not an additional validation or event replay operation. Storage/query snapshots must therefore come from the trusted persistence adapter.

## State transitions

| Operation | Allowed source / condition | Result / rejection |
| --- | --- | --- |
| Create | Valid identity and nonempty local ID | PendingSubmission; version 0; received 0; no receipts or supplier ID |
| RequireIdentity | Same client key re-entry | Exact record equality required; otherwise purchase_identity_conflict |
| ApplySupplierOutcome | PendingSubmission or SubmissionUnknown | Accepted or Rejected; save supplier ID; increment version/update time |
| ApplySupplierOutcome | Accepted, PartiallyReceived, Received | Same accepted=true and same supplier ID: no mutation; otherwise supplier_outcome_conflict |
| ApplySupplierOutcome | Rejected | Same accepted=false and supplier ID: no mutation; otherwise supplier_outcome_conflict |
| MarkUnknown | PendingSubmission or SubmissionUnknown | SubmissionUnknown; increments version and updates time even if already unknown |
| MarkUnknown | Any settled state | No mutation; never downgrade accepted/rejected/received results |
| Receive | Nonempty receipt ID and positive quantity | Validate before replay/state checks; invalid_receipt otherwise |
| Receive replay | Existing receipt in this aggregate | Same quantity returns original receipt without version/time/event change, including Received state; changed quantity conflicts |
| New Receive | Accepted or PartiallyReceived; quantity <= remaining | Append receipt, checked addition, increment version; PartiallyReceived if remaining >0, otherwise Received |
| New Receive | Other state or excessive quantity | receipt_state_conflict or over_receipt; no mutation |

The aggregate checks replay within one purchase. The persistence adapter additionally enforces global ReceiptId uniqueness across purchases/products. A matching HTTP replay can return the current order snapshot (including later receipts) together with the original receipt; the whole order response is not frozen at the first receipt. Original ReceivedAt is retained. Equivalent decimal values 100 and 100.00 are equal identity values.

## Effects and boundaries

Supplier acceptance or rejection never changes Inventory. There are no emitted Procurement domain-event objects. On a first receipt, the application-owned local commit capability atomically persists aggregate/receipt plus producer-owned `GoodsReceived`; publication is infrastructure work after commit. Domain code performs no supplier, database or broker I/O. Version is an observed aggregate counter; HTTP has no ETag/expected-version precondition. Database locks serialize mutation.

See [persistence and messaging](../adapter/persistence-and-messaging.md) for transaction/replay guarantees and [aggregate tests](../../../tests/procurement/aggregate/purchase-order.test-spec.md) for GWT expectations. Current-source assertions and missing test coverage are not runtime results.

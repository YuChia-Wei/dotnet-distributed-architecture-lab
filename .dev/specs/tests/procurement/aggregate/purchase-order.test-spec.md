# PurchaseOrder aggregate formal-test specification

Type: formal-test. Bound source `179b3e12bb1e5f1c67cee3158ccd414bd9a8b6a5`. Production subject: [PurchaseOrder](../../../domains/procurement/entity/purchase-order-spec.md). Requirement sources: BR01–BR06 / AC01–AC02 in the [original requirements](../../../../workflows/2026-09-26-procurement-supplier-lab/requirements.md). Test presence/execution rules are in the [test entry](../README.md).

Unit setup uses a fixed valid PurchaseIdentity, explicit nonempty order/receipt IDs and controlled UTC timestamps. No database, supplier or broker participates. Assert exact before/after state, version, timestamp, identity and receipt count, not just lack of exception.

| ID | Given | When | Then / observable oracle |
| --- | --- | --- | --- |
| P01 | Valid identity | Create purchase | PendingSubmission; version 0; received 0; no supplier ID or receipts |
| P03 | Existing identity | RequireIdentity with changed product/provider/SKU/quantity/price/currency | purchase_identity_conflict; original identity/state unchanged |
| P06 | Pending order and valid rejected supplier outcome | Apply rejection, then attempt receipt | State becomes Rejected; new receipt raises receipt_state_conflict and does not change quantity |
| P07 | Empty GUID, invalid SKU, quantity <=0, negative/out-of-range price, non-cent value, non-TWD or wrong provider | Create/Validate | Corresponding invalid_identity/invalid_sku/invalid_purchase before external effects |
| PS-V01 | Prices at 0 and numeric(18,2) maximum, 100 vs 100.00 vs 100.000, and 0.001 | Validate/equality | In-range numeric cent values are accepted even with trailing zero scale; non-cent value is rejected |
| PS-V02 | Pending or unknown; then accepted/rejected/partially received/received | MarkUnknown or apply matching/contradictory supplier outcome | Repeated unknown updates version/time; settled MarkUnknown does nothing; matching known outcome does not mutate; contradiction raises supplier_outcome_conflict |
| R01 | Accepted quantity 10 | Receive 6 and then 4 with distinct IDs | PartiallyReceived then Received; total 6 then 10; one version increment per new receipt |
| R02 | Unaccepted order or remaining 4 | Receive zero/negative, empty ID, or new quantity 5 | Invalid/state/over_receipt error as appropriate; no receipt or quantity/version change |
| R03 | Existing receipt, including a fully received order | Receive same ID and quantity with a later supplied timestamp | Return original receipt/time; no extra quantity, receipt or version; replay check precedes settled-state rejection |
| R04 | Existing receipt | Receive same ID with different quantity | receipt_identity_conflict; no mutation |

Global cross-order ReceiptId collision and concurrency cannot be proven by one aggregate instance; use [adapter tests](../integration/procurement-adapters.test-spec.md). Product existence and stock mutation belong to other boundaries. Aggregate does not emit domain-event objects, so do not invent a pending-events assertion.

Existing [ReceiptScenarios](../../../../../tests/Procurement.Tests/ReceiptScenarios.cs) and [PurchaseScenarios](../../../../../tests/Procurement.Tests/PurchaseScenarios.cs) provide partial executable coverage. PS-V labels are explicit verification targets without a full test-presence claim. No tests were executed by authoring.

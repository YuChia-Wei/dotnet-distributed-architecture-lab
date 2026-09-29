# Procurement specifications

This is the current formal spec entry for the single-item Procurement bounded context. It fills the domain/test directory gap left by the [original implementation specifications](../../../workflows/2026-09-26-procurement-supplier-lab/specifications.md). The original workflow remains historical evidence; it is not moved or rewritten.

Source revision: `179b3e12bb1e5f1c67cee3158ccd414bd9a8b6a5`. Reconciled on 2026-09-29 for [Issue #25](https://github.com/YuChia-Wei/dotnet-distributed-architecture-lab/issues/25). Sources are the [authorized requirements](../../../workflows/2026-09-26-procurement-supplier-lab/requirements.md), original architecture/spec/test baseline, and tracked implementation. Existing US01–US08, AC01–AC06, BR01–BR07 and P/R/S/M/U/V scenario IDs retain their original meanings and namespace. New `PS-*` labels below identify documentation coverage or verification additions, not newly approved business requirements.

These documents distinguish accepted baseline intent from observed implementation. Source recovery does not make every observed behavior desirable or prove test compliance. Conflicts requiring a product decision are listed below. This documentation delivery changes no runtime behavior, framework adoption, or test results.

## Reading map

| Contract | Specification |
| --- | --- |
| Aggregate identity, value constraints, state transitions and replay | [PurchaseOrder](entity/purchase-order-spec.md) |
| Supplier quote | [QuoteSupplier](usecase/quote-supplier.json) |
| Create or re-enter a purchase | [CreatePurchase](usecase/create-purchase.json) |
| Read one / recent purchases | [GetPurchase](usecase/get-purchase.json), [ListPurchases](usecase/list-purchases.json) |
| Reconcile original provider result | [ReconcilePurchase](usecase/reconcile-purchase.json) |
| Record physical goods receipt | [ReceiveGoods](usecase/receive-goods.json) |
| Inbound HTTP routes, DTOs, status and errors | [ProcurementController](adapter/procurement-controller.json) |
| Outbound supplier protocol and profile selection | [Supplier gateway](adapter/supplier-gateway.md) |
| SQL, transactions, receipt publication and receiving boundary | [Persistence and messaging](adapter/persistence-and-messaging.md) |
| GWT verification and existing test presence | [Procurement test specs](../../tests/procurement/README.md) |
| Inventory-owned receipt processing | [Cross-context receipt tests](../../tests/cross-domain/procurement-inventory-receipt.test-spec.md) |

Procurement owns the purchase and its receipt facts. Products owns product master data; Inventory owns stock and its receipt-processing ledger. A ProductId is a reference, not ownership of either other aggregate. SupplierSandbox and SupplierMock are external-system samples; provider modes do not define Procurement business state. Procurement has four projects (Domain, Application, Infrastructure, WebApi), no Consumer host, and uses Dapper/Npgsql. Inventory remains EF Core. The Procurement WebApi hosts its source-outbox relay.

## Requirement traceability

| Existing source | Formal coverage | Test scope |
| --- | --- | --- |
| US01–US02 / AC01 / BR01–BR03, BR06 | Identity, quote/create/get/list/reconcile, supplier gateway | P01–P07; aggregate/use-case/adapter specs |
| US03–US04 / AC02 / BR04–BR05, BR07 | Receipt, local transaction, GoodsReceived, Inventory boundary | R01–R08; receipt and cross-context specs |
| US05–US06 / AC03–AC04 | Profile selection and supplier wire contract; tool controls remain external to this BC | S01, M01–M06, U01–U03 retained in [lab test baseline](../../../workflows/2026-09-26-procurement-supplier-lab/test-specification.md) and [team guide](../../../guides/external-api-testing/README.md) |
| US07 / AC05 | Exact source bindings, contract/error tables and coverage limits | Test presence is distinguished from a run; [historical evidence](../../../workflows/2026-09-26-procurement-supplier-lab/acceptance-report.md) stays dated |
| US08 / AC06 | Original model experiment is historical | This supplement is document authoring, not a new model benchmark |

## Reconciled differences and open decisions

| ID | Older wording or expectation | Observed implementation at the bound revision | Disposition |
| --- | --- | --- | --- |
| PS-D01 | Reconcile an accepted local order returns itself | Reconcile always calls the original provider; matching outcome preserves state, contradictory outcome conflicts, and settled invalid response is surfaced | Document actual behavior; deciding to skip lookup requires separate behavior change |
| PS-D02 | BR02 says nonnegative decimal | PurchaseIdentity also limits price to 9999999999999999.99 and requires rounding to two decimal places to leave the numeric value unchanged (trailing zero scale is accepted) | Explicitly record the implemented persistence-compatible constraint |
| PS-D03 | BR06 broadly describes unknown external results | Supplier 409 and HTTP 400/422 propagate after the local identity commit; a new order can remain PendingSubmission. A valid 2xx `status=rejected` is instead a durable Rejected outcome | Preserve distinction; any new transition policy is an owner decision |
| PS-D04 | US01 operates on an existing ProductId | Procurement validates nonempty GUID but does not query Products/Inventory before creation. Missing Inventory is detected on receipt consumption | Existing product/stock is an operational precondition, not enforced cross-context admission |
| PS-D05 | Health checks essential dependencies | `/health` currently executes PostgreSQL SELECT 1 only | It does not prove schema, supplier or Kafka readiness |

No multi-line purchasing, approval, payment/refund, supplier master CRUD, tax/accounting, multi-currency, cancellation/editing/deletion of purchase identities, deployment authentication, or global message ordering is specified as implemented. No source-independent rebuild or 100% compliance is claimed: the older [reconstruction contracts](../../reconstruction/README.MD) remain a dated three-context baseline.

## Delivery and verification boundary

This is a direct, Issue-bound document delivery under `spec-author` drafting/normalization. The Issue and PR own scope/authorization/results; no independently resumable implementation task state requires another workflow. Two read-only workers invoked with GPT-6 Sol/high settings extracted domain/API and persistence/integration evidence; root wrote and reviewed this specification set. JSON required-key checks, source/link checks and a semantic cross-check are documentation validation only. No runtime tests or Docker mutations belong to this change. The RC2 framework handoff/admission gate remains separately tracked in Issue #23 and is not adopted or declared passed here.

# Procurement, supplier and receiving specifications

Type: entity + production + adapter specifications, scoped sections below. Version 1. Sources: requirements.md BR01–BR07, architecture.md. Authorized initial implementation; not an execution/compliance result.

## Entity: PurchaseOrder

Fields: Guid Id and ClientRequestId; Guid ProductId; string SupplierSku (1–64 `[A-Za-z0-9_-]`), Provider (`direct|wiremock|microcks`); positive int Quantity; decimal UnitPrice >=0; Currency `TWD`; optional vendor SupplierOrderId string; int ReceivedQuantity; int Version; state `PendingSubmission|SubmissionUnknown|Accepted|Rejected|PartiallyReceived|Received`; timestamps in UTC. Reject Guid.Empty, numeric overflow and unbounded text.

Purchase creation payload identity includes every immutable field except generated Id/timestamps/version. Same key/same payload returns the existing order; changed field is 409 with no external call. There is no edit/delete workflow. PendingSubmission/SubmissionUnknown may become Accepted/Rejected; accepted outcome never regresses due to a competing failure. Receipt replay is checked before terminal-state checks. Each new receipt uses positive quantity, cannot exceed the remaining quantity, and changes Accepted to PartiallyReceived or Received. Aggregate owns immutable receipt facts; no shared mutable list exposed.

## Production and inbound HTTP: Procurement

Base `/api/procurement`; JSON camelCase. Error shape includes stable `code` and `message`; invalid input 400, missing resource 404, identity/concurrency/state/over-receipt conflict 409, provider transport unavailable outcome represented durably as SubmissionUnknown with 202. Never expose stack traces/connection strings. Created order 201, identical established replay 200. Cancellation after provider side effects cannot erase durable pending identity.

| Method/path | Input | Result / effect |
| --- | --- | --- |
| GET `/suppliers/{provider}/catalog/{sku}` | configured provider, valid SKU | quote `{sku,name,unitPrice,currency,origin}`; unknown SKU 404, unreachable 502/504 with explicit code |
| POST `/purchase-orders` | `{clientRequestId,productId,supplierSku,quantity,unitPrice,currency,provider}` | create/persist identity, call supplier outside transaction, record outcome, return order |
| GET `/purchase-orders` | none | bounded recent orders, maximum 100 |
| GET `/purchase-orders/{id}` | Guid | order with receipts and current status |
| POST `/purchase-orders/{id}/reconcile` | empty body | GET supplier by original clientRequestId, apply verified identity-matching outcome; absent/transport leaves unknown; accepted local order returns itself |
| POST `/purchase-orders/{id}/receipts` | `{receiptId,quantity}` | 201 new / 200 matching replay with receipt and resulting order; atomic aggregate+receipt+outbox, no HTTP Inventory call |

Expose explicit IOperationUseCase application ports to controllers/handlers. Query/read behavior may use query ports. ISupplierGateway uses application DTOs; vendor DTOs stay in Infrastructure. Repository/committer ports must represent local capability/aggregate operations, not arbitrary connection/transaction access.

## Adapter: external supplier API v1

Real, WireMock and Microcks share these provider routes and DTO shapes; no direct reference to internal BC contracts.

| Method/path | Input | Output |
| --- | --- | --- |
| GET `/supplier/catalog/{sku}` | SKU | `{sku,name,unitPrice,currency,origin}` |
| POST `/supplier/orders` | `{clientRequestId,sku,quantity,unitPrice,currency}` | `{supplierOrderId,clientRequestId,sku,quantity,unitPrice,currency,status,origin}`; status `accepted|rejected` |
| GET `/supplier/orders/by-client-request/{clientRequestId}` | Guid | same order response or 404 |

Sandbox persists orders in its own PostgreSQL database. Idempotency is a unique clientRequestId + exact typed payload. `REAL-001` is a real catalog SKU (TWD 100), `MOCK-001` has the same price but is reserved for mock examples; `DENY-001` permits deterministic business rejection. Unknown SKU 404 for quote, explicit rejection/400 for order. Quantity >0, price/currency must match its quote; no arithmetic/truncation surprises. Repeated rejected requests retain a stable rejection; changed payload returns 409. Concurrent requests create one order and keep its supplierOrderId stable. All successful sandbox responses include origin `sandbox` and header `X-Supplier-Origin: sandbox`; mocks identify `wiremock` or `microcks`.

Sandbox local controls: GET `/sandbox/requests` returns at most 100 recent safe request observations with timestamp/method/path/clientRequestId where available; GET/PUT `/sandbox/control` reads/sets bounded `delayAfterCommitMs` (0–10000), applied only after a POST order commits. GET query stays responsive for reconciliation. Control defaults to zero on startup and UI says whether transient. No log of arbitrary credentials/headers. Root UI documents/sample calls and can inspect orders, request provenance and fault control.

The gateway verifies response identity (clientRequestId, sku, quantity, price, currency), allowed status and nonempty supplierOrderId before accepting it. Invalid/malformed/mismatched response maps to SubmissionUnknown, never stock mutation. Explicit supplier 409 is an identity conflict, not a successful replay. HTTP timeouts/network errors/5xx are indeterminate. Do not use unconditional automatic POST retry; explicit same-key re-entry is safe. Reconcile must preserve previously accepted vendor identity and report contradictory responses.

## Adapter: receipt event and Inventory

New producer-owned contract namespace `Lab.BoundedContextContracts.Procurement.IntegrationEvents`, type `GoodsReceived`: Guid ReceiptId, PurchaseOrderId, ProductId; positive int Quantity; DateTimeOffset ReceivedAt. ReceiptId is event/message identity. Topic `procurement.integration.events`. Partition by normalized ProductId. Envelope can redeliver; no global ordering promise. Versioned schema documented as v1; vendor DTOs never used as internal integration events.

Inventory inbound Consumer handler maps exactly once to an application receipt use case. Inventory owns its own input/result types and capability port. Transaction: claim receipt ID, reject changed PO/Product/Quantity, lock/verify existing InventoryItem, increment stock through domain behavior, store receipt result and Inventory source outbox event, commit once. Matching terminal replay returns original resulting stock and stages nothing (including after outbox retention). Failed missing-product operation must be retriable after stock initialization; rollback removes incomplete claims. Checked integer overflow rejects without partial state. Consumer conflict is diagnosable and must not acknowledge it as business success. Use existing bounded failure policy rather than infinite immediate loops.

New Inventory SQL receipt table and migration are additive, idempotent; mirror mappings in EF DbContext. Use existing StockIncreased semantic or a clearly new receipt-specific stock event, never StockReturned. If introducing a new inventory event type register it in the outbox relay allowlist. Do not change existing API/stock/reservation behavior.

## Adapter: native mocks and lab controls

SupplierMock.WebApi owns WireMockServer plus its admin facade/control Web UI. Admin requests remain local/internal. Modes `mock|proxy|hybrid`: all supported routes are mock in mock mode; proxy all in proxy mode; `MOCK-001` quote/order mock and real SKU proxy in hybrid. Query mock identity must be documented/predictable (e.g. one fixed fixture clientRequestId) and preserve request-response identity. Control exposes actual mappings/recent requests and lets user reset documented presets. UI labels transient changes; preset files and API commands are documented. Startup validation rejects unknown mode or unsafe configured upstream. Tool-native proxy must forward, not application code emulating a supplier response.

Microcks supplies checked-in OpenAPI 3.0 artifacts with examples for quotes/orders/query and mock origin. JSON body or URI dispatch selects explicit examples, with PROXY_FALLBACK to sandbox for unmatched responses on known operations; a PROXY variant forwards all, mock variant does not forward. Import/config scripts identify API name/version and resulting URL without hard-coded undocumented assumptions. Unknown imported route behavior is tested/documented independently; do not claim global catchall. UI changes/JSON edits and reimport behavior must be reproducible. Native proxy path rewrite and origin/request evidence are runtime acceptance items.

## Operational and persistence contracts

Procurement SQL migration initializes its own tables; seed never drops existing data. Sandbox uses a separate database/schema owner from Procurement. Source outbox cannot lose a committed receipt if broker is unavailable. Startup health endpoints `/health` are available on each new host; ready state checks essential dependencies. Observability includes PurchaseOrderId/ReceiptId/clientRequestId, route profile and outcome without credentials. Retain standard cancellation/timeouts and bounded request/list/log sizes.

Model work ownership and retries are recorded in workflow execution notes. This specification is the first implementation baseline; coordinator corrections must update it before asking an implementer to follow changed semantics.

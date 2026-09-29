# Supplier HTTP adapter specification

Type: outbound adapter. Source revision `179b3e12bb1e5f1c67cee3158ccd414bd9a8b6a5`; [authority and differences](../README.md). Requirements AC01/AC03, BR01/BR06. Source: [HttpSupplierGateway](../../../../../src/Procurement/DomainCore/Procurement.Infrastructure/HttpSupplierGateway.cs), [application port](../../../../../src/Procurement/DomainCore/Procurement.Applications/ProcurementOperations.cs), [host configuration](../../../../../src/Procurement/Presentation/Procurement.WebApi/Program.cs).

## Profile and protocol

`ISupplierGateway` is an application-owned port. Infrastructure owns supplier wire DTOs. It selects named clients `supplier-direct`, `supplier-wiremock`, `supplier-microcks` from immutable purchase Provider. Base URLs come from `SupplierProfiles:*`, must be absolute HTTP(S), and get a trailing slash. Request data cannot choose an arbitrary upstream URL. The host requires integer `SupplierHttp:TimeoutSeconds` in 1..30 (default 2). There is no configured automatic POST retry policy.

| Operation | Relative path and payload | Output |
| --- | --- | --- |
| QuoteAsync | GET `supplier/catalog/{escaped SKU}` | sku, name, unitPrice, currency, origin |
| SubmitAsync | POST `supplier/orders`; clientRequestId, sku (mapped from SupplierSku), quantity, unitPrice, currency | supplierOrderId, clientRequestId, sku, quantity, unitPrice, currency, status, origin |
| LookupAsync | GET `supplier/orders/by-client-request/{clientRequestId:D}` | Same order response, or explicit NotFound |

Relative paths preserve a Microcks API/version base-path prefix. ProductId and local PurchaseOrderId are not supplier wire fields. JsonSerializerDefaults.Web applies. Decimal equality is numeric; equivalent 100/100.00 is accepted.

## Validation and error mapping

Before quote HTTP, the adapter validates provider and SKU through a temporary PurchaseIdentity; an invalid SKU raises invalid_sku. Quote responses require exact requested SKU, currency TWD, nonnegative price and nonblank name/origin. Quote validation does not apply the full purchase price precision/cap; creating a purchase does. Order responses require exact original clientRequestId, SKU, quantity, decimal unit price and currency; literal status `accepted` or `rejected`; nonblank supplierOrderId <=128 and nonblank origin. Malformed/null/mismatched responses raise supplier_invalid_response. A valid 2xx rejected order is a known `Accepted=false` outcome, not a transport failure.

| Condition | Adapter result |
| --- | --- |
| Unknown named provider | ProcurementRuleException invalid_purchase |
| Quote HTTP 404 | supplier_not_found |
| Lookup HTTP 404 | SupplierLookup.NotFound, not proof that a timed-out POST never committed |
| Submit / lookup HTTP 409 | supplier_identity_conflict |
| Submit HTTP 400 or 422 | supplier_business_rejection |
| Other non-2xx HTTP 408 or 504 | supplier_timeout |
| Other non-2xx (including 5xx) | supplier_unavailable |
| OperationCanceledException caused by caller cancellation | Propagate cancellation |
| Other OperationCanceledException / HttpRequestException | supplier_timeout / supplier_unavailable |
| Invalid JSON or invalid successful response | supplier_invalid_response |

Create/reconcile have their own handling of these outcomes; consult the use-case JSON before inferring an inbound HTTP status. `SupplierLookupKind.Unknown` is supported at the port boundary; the current HTTP adapter ordinarily returns Found/NotFound or throws.

Origin is only checked for nonblank text. The gateway does not authenticate its value, check it against the chosen profile, or validate `X-Supplier-Origin`. For proxy proof, separately observe native mappings/operations and Sandbox request records. Quote GET has no clientRequestId and requires isolated SKU/time correlation. Control-plane mode changes do not rewrite existing purchase Provider.

## External sample boundary and verification

Sandbox owns its database and supplier-key idempotency. Concurrent Procurement calls can create multiple HTTP attempts for one key; one logical supplier order relies on that external contract. WireMock.Net and Microcks implement the same wire shapes but have different unmatched-request behavior; Microcks fallback is limited to imported known operations. Fixed POST mock identity includes every top-level field, not SKU alone.

These sample/control details are maintained in the [lab operations guide](../../../../operations/procurement-supplier-lab.md), [comparison](../../../../guides/external-api-testing/solution-comparison.md), and [original S/M/U scenarios](../../../../workflows/2026-09-26-procurement-supplier-lab/test-specification.md). They do not become extra Procurement aggregates. [Adapter tests](../../../tests/procurement/integration/procurement-adapters.test-spec.md) distinguish fake HTTP matching tests from actual two-engine proxy observations. No runtime run is claimed by this adapter document.

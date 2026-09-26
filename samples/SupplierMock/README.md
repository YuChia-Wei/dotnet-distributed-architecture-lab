# Supplier Microcks artifacts

These OpenAPI 3.0.3 files import the same external provider contract as the sandbox:

- `microcks/supplier-mock.yaml` has fixture examples without proxy dispatchers.
- `microcks/supplier-proxy.yaml` sets each known operation to native `PROXY`.
- `microcks/supplier-hybrid.yaml` uses operation-level `PROXY_FALLBACK`: the `MOCK-001` catalog fixture and the fixed order fixture are mocked; unmatched requests on those known operations are forwarded to the sandbox. Unknown paths remain Microcks misses because dispatchers apply per operation, not as a global reverse proxy.

## Import and reset

Open the Microcks UI (the lab compose maps it to `http://localhost:8184`), choose Quick Import, and upload exactly one of the three files. Confirm the discovered API name `Supplier API` and version `1.0.0` in **APIs | Services**. After changing a file or mode, upload that same artifact again; its operation-level `x-microcks-operation` values are the repeatable reset source. The built-in Microcks UI is the control surface; this repository does not present a fake Microcks dashboard.

The resulting mock base path is `/rest/Supplier+API/1.0.0`. For example, the quote operation is `/rest/Supplier+API/1.0.0/supplier/catalog/MOCK-001`. If the UI reports a different imported API identity, use the displayed name/version when composing that prefix. The fixed mock-order example uses clientRequestId `9d4c99da-6517-46b2-baa7-7e81106d3d34`, SKU `MOCK-001`, quantity 2, price 100 TWD, and fixed supplierOrderId `00000000-0000-4000-8000-000000000017`; keep those values together so the response preserves request identity.

For hybrid dispatch, Microcks' `PROXY_FALLBACK` uses its native per-operation rules: `URI_PARTS` for path parameters and `JSON_BODY` for the fixed order example. Proxy URL is the configured internal service origin `http://supplier-sandbox:8080/`; the request path is appended by Microcks. Use the deployed internal sandbox service name if compose assigns another name. The sandbox request journal and `X-Supplier-Origin` response header are evidence that an unmatched known operation reached the real upstream. Reaching an undocumented route is a separate expected miss.

These are fixture contracts. Verify upload/import status and real proxy behavior in the selected Microcks container during runtime acceptance; file parsing or successful mock responses do not prove proxy forwarding.

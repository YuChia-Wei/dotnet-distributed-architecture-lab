# Procurement integration architecture

Status: coordinator-selected initial implementation under the owner's 2026-09-26 authorization; final owner review pending. Sources: requirements.md US01–US08, current target architecture and live tracked HEAD cc0e345.

## Ownership and dependencies

- Products retains product identity. Purchase input references an existing ProductId; this slice does not duplicate the product catalog.
- Procurement owns PurchaseOrder, immutable submission identity, provider outcome, physical goods receipts and the receipt source outbox. Domain and Application contain no HTTP, Wolverine, Dapper or Npgsql types.
- Inventory owns stock and receipt deduplication. Its dedicated receipt port commits stock, outcome ledger and producer-owned stock-increased event together. Existing Restock/StockReturned is unchanged.
- SupplierSandbox.WebApi is an external provider with its own orders/storage and vendor DTOs; it does not reference Procurement Domain or write Inventory.
- Supplier HTTP adapter implements application-owned ISupplierGateway; named configured profiles direct/wiremock/microcks only. Store the profile on each purchase order so reconciliation returns to the original configured provider route.
- Purchase receiving emits Procurement-owned GoodsReceived v1 via source outbox and Kafka `procurement.integration.events`. Inventory's Consumer maps the event to its application receipt input. Delivery is at least once; the durable receipt key provides one stock effect.

Proposed physical roots: `src/Procurement/DomainCore/{Procurement.Domains,Procurement.Applications,Procurement.Infrastructure}`, `src/Procurement/Presentation/Procurement.WebApi`, `src/BC-Contracts/Lab.BoundedContextContracts.Procurement`, `samples/SupplierSandbox/SupplierSandbox.WebApi`, `samples/SupplierMock/SupplierMock.WebApi`. The mocks and sandbox are supporting lab systems, not shared domain libraries.

## Selected consistency model

Procurement uses Dapper/Npgsql/PostgreSQL, no event sourcing. A purchase order and its owned receipts are one aggregate. Persist creation before external submission. HTTP is outside the database transaction. A receipt update atomically persists the aggregate, receipt identity and pending outbox event. Optimistic version checks or a short row lock serialize conflicting receipt writes; business invariants stay in Domain/Application. Capability-specific repository/committer ports own transaction completion in Infrastructure. No cross-context transaction and no default application IUnitOfWork.

Concurrent identical submissions may reach the supplier more than once using the same idempotency key; the supplier must return one order. A late transport failure must not downgrade an already accepted local order. An accepted/rejected order is terminal for submission. Reconcile performs GET first; a true provider 404 leaves outcome unknown, allowing an explicit safe same-key retry through the submit use case. HTTP timeout is configurable (demo 2 seconds); 4xx business rejection, 409 identity conflict, 5xx/timeout/invalid response remain distinct.

The outbox relay preserves a stable GoodsReceived event ID equal to ReceiptId; process restarts or send-before-mark crashes can repeat delivery, never silently discard the row. Bounded retry metadata and diagnosable failed state are required. Inventory exact replay returns the original outcome without event factory/staging, even after a published outbox row was removed. Conflicting receipt payload is rejected, not interpreted as an already applied success.

## Native mock/proxy behavior and controls

Microcks `quay.io/microcks/microcks-uber:1.15.0` JVM provides native UI, imported OpenAPI operations, `PROXY` and `PROXY_FALLBACK`. Fallback is per known operation and response matching; it is not a global unknown-route reverse proxy. Supply importable mock/proxy/hybrid API artifacts or a script selecting the operation dispatcher; preserve the same provider path/contract and document Microcks' mock URL prefix.

WireMock.Net 2.15.0 runs in a dedicated .NET host. Narrow mock mappings use priority 1; native upstream proxy catchall uses priority 10 in hybrid mode. Proxy-only removes/omits mocks; mock-only omits proxy. A companion Web UI in the same host exposes three fixed profiles, actual mappings and recent request logs using Admin API. It must explicitly show the current mode and upstream. Restrict upstream to the configured sandbox, avoid generic arbitrary-URL forwarding. Preserve request method/path/query/body/content type; test path joining rather than assuming it.

Built-in Microcks UI is reused; no pretend WireMock.Net built-in web dashboard. The custom control page identifies itself as this repository's lab UI and links Microcks, Sandbox and Procurement API/control pages. JSON presets are source-controlled; startup reapplies the documented initial mode. Runtime edits are visibly transient unless exported to a preset.

## Deployment and compatibility

Use an additive `docker-compose.procurement.yml` file/profile with new services and dedicated named database volume(s), reusing existing Inventory/Kafka when started with the existing base/override files. No volume removal/reset and no changes to existing defaults just to run this lab. New public demo ports bind 127.0.0.1. Existing consumer behavior, API routes and serialization contracts remain compatible. Add necessary YARP routes only in the lab overlay/config or document direct localhost entrypoints. SQL migration is additive and repeatable, also works for an existing Inventory DB.

## Alternatives and reasons

| Choice | Benefit | Cost / selected disposition |
| --- | --- | --- |
| Only mocks, no supplier | Smaller scope | Rejected by explicit owner request; cannot observe real upstream forwarding. |
| Same behavior through Microcks and WireMock.Net | Comparable client contract and native fallback demos | Selected; mappings/config syntax remain tool-specific. |
| Direct HTTP inventory update | Fewer components | Not selected; existing Kafka/outbox lab should demonstrate durable receipt delivery. |
| Full purchasing ERP or payment orchestration | Broader domain | Out of scope; single-line PO gives bounded but meaningful idempotency/receipt behavior. |

## Verification and sources

Behavior/mapping tests plus real PostgreSQL/Kafka/HTTP/container flow are required separately. Browser verification checks controls render and work; logs/provenance prove proxy execution. Mock/schema tests cannot substitute for real message delivery.

- https://microcks.io/documentation/explanations/dispatching/
- https://microcks.io/blog/new-proxy-features-1.9.1/
- https://microcks.io/documentation/guides/usage/custom-dispatchers/
- https://microcks.io/documentation/references/container-images/
- https://wiremock.org/dotnet/proxying/
- https://wiremock.org/dotnet/admin-api-reference/
- https://github.com/WireMock-Net/WireMockInspector (separate desktop tool, not required for the custom Web UI)

Documentation research confirmed capabilities; local execution remains required before acceptance. Graph discovery was partially stale (Dapper snippets for now-EF Inventory); tracked source is the authority.

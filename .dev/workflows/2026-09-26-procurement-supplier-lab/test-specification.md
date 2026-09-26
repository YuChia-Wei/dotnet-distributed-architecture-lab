# Procurement lab formal-test specification

Version 1. Owner: spec-author. Scope: requirements.md AC01–AC06 and specifications.md. Authoring is not execution. Plain xUnit v3, recognizable Given/When/Then step methods, target-selected NSubstitute for new projects (or hand-written deterministic port fixtures), Moq/NSubstitute preserved per existing project.

## Scenario inventory

| ID | AC | Level | Given / When | Then assertions |
| --- | --- | --- | --- | --- |
| P01 | AC01 | Domain/use case | valid real SKU, qty10 / create PO | persisted identity, supplier called with original clientRequestId, accepted order/vendor ID |
| P02 | AC01 | Use case + PG | same key/same payload / repeat | same local and supplier identity; no second logical order |
| P03 | AC01 | Use case + PG | same key changed quantity/provider/product / repeat | 409 identity conflict; stored original unchanged; no second external submission |
| P04 | AC01 | HTTP + PG | sandbox delays response after commit beyond timeout / submit then reconcile | durable unknown after timeout, exactly one upstream order, GET recovers accepted; no stock yet |
| P05 | AC01 | Use case | 5xx, malformed body, mismatched identity, unknown status / submit | SubmissionUnknown; no false acceptance; stored attempt remains |
| P06 | AC01 | Domain/use case | DENY-001 / submit, receive | rejection recorded; receipt forbidden |
| P07 | AC01 | Unit/HTTP | empty GUID, invalid SKU, qty<=0, negative price, non-TWD / submit | validation rejection before outbound/database effects |
| R01 | AC02 | Domain + E2E | accepted qty10 stock20 / receive6 then4 with distinct IDs | partial then complete; durable receipts; eventual stock26 then30 |
| R02 | AC02 | Domain + PG | remaining4 / receive5 or zero/negative | rejection; quantity/receipt/outbox unchanged |
| R03 | AC02 | PG + Kafka | receipt previously applied / replay same receipt repeatedly | one stock increment and one original event; outcome replay after outbox deletion creates no new outbox row |
| R04 | AC02 | PG | same ReceiptId changed PO/product/quantity / replay | identity conflict and no mutation |
| R05 | AC02 | PG | same receipt concurrent / apply | one claim/result/increment; all matching callers obtain stable outcome |
| R06 | AC02 | PG | two receipts race exceeding remaining / receive | accepted sum <= ordered; losing request rejected/retry-safe |
| R07 | AC02 | PG | unknown product or forced transaction failure / apply then retry when valid | no partial claim/stock/outbox; later valid retry succeeds once |
| R08 | AC02 | Actual broker | Kafka temporarily unavailable / commit receipt then restore | durable pending outbox survives and eventually delivers; no duplicate stock effect |
| S01 | AC01 | Sandbox PG/HTTP | repeated and concurrent same supplier key / POST | one persisted order stable ID; changed payload conflicts |
| M01 | AC03 | Actual HTTP | hybrid WireMock + MOCK-001 / GET quote | mock origin; sandbox request count unchanged |
| M02 | AC03 | Actual HTTP | hybrid WireMock + REAL-001 / GET quote and POST order | sandbox origin and corresponding logged upstream request; body/path preserved |
| M03 | AC03 | Actual HTTP | Microcks PROXY_FALLBACK + matching example / request | microcks origin; no upstream request |
| M04 | AC03 | Actual HTTP | Microcks PROXY_FALLBACK + unmatched known operation / request | sandbox origin and matching upstream path/body observation |
| M05 | AC03 | Actual HTTP | each platform proxy-only / request formerly mocked SKU | real upstream reached |
| M06 | AC03 | Actual HTTP | each platform mock-only / unmatched response/unknown route | documented mock miss/error; sandbox count unchanged |
| U01 | AC04 | Browser + API | running controls / switch WireMock mode and inspect mappings/log | visible selected mode, actual native mappings and observed request; startup/reset semantics shown |
| U02 | AC04 | Browser + HTTP | Microcks running/imported / open UI and inspect operation | native UI visible and operation mock/proxy settings documented; supplied import/reset procedure works |
| U03 | AC04 | Browser | Supplier root / inspect order/request and configure bounded delay | actual sandbox controls work, provenance visible, malformed delay rejected |
| V01 | AC05 | Build/regression | complete code / run focused and existing tests | no regressions; skips and external opt-in reported separately |
| V02 | AC06 | Evidence/review | worker deliveries / parent reviews and worker remediates | actual model inputs/results/findings retained, unresolved findings not called passed |

## Environment, assertions and isolation

Unit/application tests use concrete subjects and mock only outbound ports. Real PostgreSQL tests use unique identities and clean only their own rows; dedicated new DB volumes do not replace actual persistence semantics. Existing Inventory external tests remain opt-in via RUN_EXTERNAL_INTEGRATION_TESTS and INVENTORY_TEST_POSTGRES_CONNECTION_STRING. New real integration tests follow the same opt-in convention. No production/synthetic evidence conflation.

HTTP mock/proxy acceptance runs real Microcks, real WireMock.Net and real SupplierSandbox. Baseline and final sandbox observations, request identity and origin prove forwarding rather than status-only checks. Sequential steps in P04/R01 are intentional multi-operation scenarios. Broker recovery R08 may stop/start only the lab's explicitly selected Kafka service, preserving volumes and unrelated containers. If runtime is unavailable record not-executed/blocked; do not waive it by replacing the check with mocked transports.

Every test maps its scenario IDs in a comment/trait and uses Given/When/Then calls (not just comments). An execution report maps AC and scenario IDs to exact command, actual subject, outcome, assertions and retained output; no prospective passes. Parent reviews domain ownership, idempotency race windows, transaction boundaries, native proxy behavior and UI behavior. All required criteria need evidence before claiming compliant-within-scope. Owner final review remains a separate decision.

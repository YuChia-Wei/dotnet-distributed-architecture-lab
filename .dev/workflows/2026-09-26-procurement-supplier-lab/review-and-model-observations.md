# Coordinator review and model observations

Workflow: 2026-09-26-procurement-supplier-lab. Issue: #17. Review is ongoing; this is not an acceptance or owner-approval receipt.

The workers received the same committed specification baseline, `7259397`, with bounded path ownership and actual `gpt-6-sol/high` or `gpt-6-luna/high` invocations. The coordinator owns integration and review. These tasks differ in difficulty and scope; observations do not establish a controlled model ranking. Runtime token, cost and wall-clock measurements are unavailable.

## Inventory receipt slice — GPT-6 Sol / high

First delivery: `83f4f7d` with shared-contract dependency `fd6f351` (equivalent to `2d122b6`, integrated as `f7e5063`). Worker-reported initial validation: Consumer build succeeded; Inventory test suite 37 passed and 27 external tests skipped. Seven new local cases passed; seven new PostgreSQL cases remained unexecuted. The first `--no-restore` attempt failed with NETSDK1004 because the isolated checkout had no restored assets; normal restore resolved that setup failure.

Selected review routes: use case, repository, outbox, message handler, test and general C#. Effective target packets were resolved before review. Relevant standards include domain invariant ownership, capability-specific transaction completion, `MESSAGING-TX-001`, `TEST-GWT-001`, `TEST-BDDFY-001` and target plain-xUnit selection. The explicit design commits receipt identity, stock and outgoing intent in one local transaction; durable transport receipt and later inbox completion remain distinct from that business transaction. Matching business replay bridges a crash between those stages.

| ID | Category | Evidence and practical effect | Disposition |
| --- | --- | --- | --- |
| INV-01 | MUST FIX | Distinct concurrent receipt test assumed quantity 2 always acquires the lock before quantity 3. Both intermediate stocks 7 and 8 are valid from stock 5; final stock must be 10. The assertion could fail on a correct implementation. | Sent to worker for correction. |
| INV-02 | MUST FIX | Consumer Dockerfile's pre-restore COPY list lacked the newly referenced projects and their dependencies. A local build did not validate the container build path. | Sent to worker for correction. |
| INV-03 | MUST FIX | Consumer selected the same Wolverine storage schema as the separately deployed Inventory API, which lacks the new receipt handler. Isolate consumer durability ownership from API recovery. | Sent to worker for a consumer-specific schema; runtime verification pending. |
| INV-04 | SHOULD FIX | New public API summaries were English or missing although target C# guidance selects Traditional Chinese summaries. | Sent to worker for correction. |

INV-03 is supported by the separate-schema guidance in [Wolverine PostgreSQL integration](https://wolverinefx.io/guide/durability/postgresql). Also requested a check of the existing InMemory consumer profile after adding receipt dependencies; no runtime failure is asserted without evidence.

Review repair `4098819` (integrated as `f4befe9`) addresses INV-01 through INV-04. The coordinator inspected the changed assertions, Dockerfile and schema selection. Worker reported 7 focused local passes, 7 PostgreSQL skips, and a successful InMemory Consumer startup followed by a clean stop. Container and external behavior remain pending. Initial implementation integrated as `c751276`.

Observed strengths in the first delivery: permanent business receipt identity, replay before mutation, row locking, overflow protection, rollback-capable atomic ledger/stock/outbox writes, and no event-factory call on a completed replay. Actual PostgreSQL, broker recovery and complete consumer-host behavior remain required before acceptance.

## Other slices and integrated acceptance

Procurement and supplier/mock workers remain active. Their first deliveries, corrections and exact execution results will be appended when available. The coordinator has not declared specification compliance, native proxy acceptance or browser acceptance.

The coordinator also gave the supplier worker pre-delivery feedback about native WireMock mapping field names/JSON bodies, a JavaScript mode-label name collision, and the Microcks URI dispatcher example key. This is assisted development evidence, not an unaided first-pass model result.

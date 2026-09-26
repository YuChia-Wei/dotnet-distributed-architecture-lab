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

## Procurement slice — GPT-6 Sol / high

First delivery: `79437e8`, integrated as `31a908d`. Worker-reported WebApi build: zero warnings/errors; focused tests: 20 passed, one PostgreSQL test skipped. The worker reported and repaired a NuGet scratch-lock setup failure and an xUnit v3 ValueTask compile failure. No actual PostgreSQL, Kafka or supplier run was claimed.

| ID | Category | Evidence and practical effect | Disposition |
| --- | --- | --- | --- |
| PROC-01 | MUST FIX | Application catches `HttpRequestException`, contradicting the explicitly transport-independent Application contract. Normalize provider transport failures in Infrastructure. | Repair requested. |
| PROC-02 | MUST FIX | Controller directly invokes outbound supplier/query ports; query results and HTTP output expose mutable aggregates. Selected spec requires inbound use cases and query DTOs. | Repair requested. |
| PROC-03 | MUST FIX | R06 races two quantity-6 receipts after receiving 6 of 10; both are already invalid individually, so this does not exercise concurrent oversubscription. | Race two individually valid quantity-4 receipts and assert one winner. |
| PROC-04 | MUST FIX, confirmed at runtime | The first-delivery PostgreSQL run failed when Dapper tried to materialize the positional receipt constructor using a UTC DateTime column. | Explicit persistence rows and UTC conversion added in `cabd056`; real PostgreSQL repair verification is pending below. |
| PROC-05 | MUST FIX | Supplier HTTP timeout is hardcoded despite the selected configurable timeout contract. | Bounded configuration with demo default two seconds requested. |
| PROC-06 | SHOULD FIX | Missing target aggregate marker and public Traditional Chinese API summaries reduce conformance to selected target architecture/style. | Bounded correction requested. |

PROC-04 uses the documented [Npgsql timestamp mappings](https://www.npgsql.org/doc/types/datetime) as a hypothesis source, not a substitute for the actual adapter test. The relay's source `published_at` represents durable handoff to Wolverine's transport outbox; broker delivery must be observed separately. Outage acceptance will inspect both stores and final Inventory state.

## Supplier slice and integrated acceptance

Integration and acceptance remain active. The coordinator has not declared overall specification compliance or browser acceptance.

The coordinator also gave the supplier worker pre-delivery feedback about native WireMock mapping field names/JSON bodies, a JavaScript mode-label name collision, and the Microcks URI dispatcher example key. This is assisted development evidence, not an unaided first-pass model result.

Additional pre-delivery supplier feedback identified a quote persistence/response constructor mismatch, missing origin headers on successful GET responses, and quote validation preceding an already-bound supplier idempotency key (which would misclassify a changed-price replay). Corrections and actual PostgreSQL/HTTP results remain pending.

## Actual integration checkpoints

The first Procurement delivery was built into `mqarchlab-procurement-first-delivery-tests:17` from coordinator checkout `c757dfd` (the Procurement subject remained `79437e8`). The actual same-network PostgreSQL run returned **20 passed, 1 failed, 0 skipped**, exit 1. TRX: `artifacts/procurement-lab/first-procurement-tests/_39081a7221c7_2026-09-26_03_13_22_net10.0.trx`. Failure: Dapper required a constructor with `System.DateTime receivedat`; `GoodsReceipt` accepted `DateTimeOffset`. The test setup had occurred before its cleanup block, leaving one PendingSubmission fixture. The coordinator verified and deleted only that fixture using its exact order/client identities and untouched state. The repaired test moves setup inside cleanup protection. This failed evidence is retained rather than replaced by the later result.

Procurement repair `cabd056` (integrated `4375495`) addresses PROC-01–PROC-06, adds normalized gateway cases and immutable inbound query projections. Worker result: 28 passed, 2 PostgreSQL skips. Review then found a missing target `IQueryRepository` marker and a read-consistency window between loading an order row and loading receipts. Repair `90d1389` (integrated `6e318bc`) adds the marker and RepeatableRead snapshots, plus a concurrent reader/receiver PostgreSQL scenario. Worker result: 28 passed, 3 PostgreSQL skips. Its first build failed CS0012 for a missing direct marker-assembly reference and was repaired. The final focused build had zero warnings/errors; shared BuildingBlocks CS8618 remains an existing full-build warning.

Inventory actual container build and startup succeeded. The additive receipt migration was applied; the Consumer created its dedicated `inventory_consumer_messages` durability schema and subscribed to `procurement.integration.events`. The source changes remain `4098819` / coordinator `f4befe9`. This closes INV-02/INV-03 host-wiring concerns; PostgreSQL behavior and broker recovery are separately assessed.

Supplier first committed delivery is `47db2c3` (integrated `abeedde`), GPT-6 Luna/high, with prior coordinator assistance described above. Worker tests: native WireMock HTTP against a real local Kestrel upstream passed; sandbox SKU unit test passed; one sandbox PostgreSQL test skipped. All three YAML artifacts parsed after a repaired YAML syntax error. These static checks did not establish Microcks behavior.

On 2026-09-26, the coordinator deployed the services in `mqarchlab-pr5-integration` and ran `python -B scripts/procurement-lab/test_contracts.py --output artifacts/procurement-lab/http-contracts-first.json`. **P02/P03/P04/P07, S01 and M01–M06 for WireMock passed**. **Microcks M01–M05 failed**, M06 passed. Import returned 201 but URI examples did not match the requested fixture; unmatched POST selected the fixed response; native proxy copied upstream chunked-transfer headers and the Python client reported IncompleteRead. Different upload filenames also accumulated example sources under one API version. All failures remain recorded, and repairs are assigned to the owning workers. No native Microcks success is inferred from import alone.

The first `Start-Lab.ps1` run built and started services but returned failure when an omitted nullable Guid parameter incorrectly enabled an Inventory readiness probe with an empty route segment. This is a script failure, not a service startup pass. A bounded parameter-guard repair is assigned to T005.

The actual direct purchase/receipt flow passed: dedicated retained Products fixture `d6de1326-d34a-480d-8f7d-5dd80ced1254`, initial stock 20, supplier acceptance left stock 20, receipt 6 produced 26, matching replay returned 200/created=false and stock 26, receipt 4 produced stock 30 and purchase state Received. Evidence: `artifacts/procurement-lab/direct-flow.json`, observed `2026-09-26T03:24:23.7785705+00:00`. The fixture was inserted into the existing Products test database; this does not claim a new Products API scenario. Existing product/stock rows were not reset.

Disposable Docker build/run logs are under the owner-preferred RAM disk `F:\git-worktree\procurement-lab-evidence`. Review documents and final retained evidence stay in the repository. Existing managed worker checkouts were not relocated during active work.

The first full solution regression image (source `6e318bc`, image manifest `sha256:da89a2544d3157f0142f84ec6f2d04c284407db54f76764f0b72ad09a8d771ad`) built successfully with 18 existing/shared warnings, then reported **175 passed, 2 failed, 4 skipped**. Inventory passed all 64 tests including actual PostgreSQL cases. Products and Orders suites passed. Four external EF/Wolverine sample scenarios were not configured and remain skipped, not passed. The coordinator temporarily stopped the lab's background relay hosts to avoid consuming owned database fixtures and restored them afterward. Compose `start` also started the same lab's previously stopped collector through dependency traversal; the coordinator verified its project label and returned that collector to its original stopped state. The protected `ai-collaboration-observability` project was not selected by these commands.

The two Procurement failures at this checkpoint were:

- **PROC-07, MUST FIX:** R06 expected only `over_receipt`; after one competitor fills the order, `receipt_state_conflict` is also a valid loser outcome. The repaired assertion still requires exactly one winner and unchanged final receipt/outbox totals.
- **PROC-08, MUST FIX:** initial receipt responses used .NET 100-nanosecond timestamps, while PostgreSQL truncated them to microseconds. Matching replay therefore returned a slightly different immutable receipt timestamp. Repair `2d7114f` (integrated `0946879`) creates receipts at explicit UTC millisecond precision, preserving exact HTTP, stored, replay and event values; equality assertions remain strict. The specification now records this precision contract.

Test-only repair `2bec95c` (integrated `feee507`) also covers concurrent purchase creation, persisted immutable-field conflicts, invalid receipt rollback, replay after deleting the owned source-outbox row, and receipt identity conflict across two orders/products. The worker's first unconstrained host test run stalled; only its identified MSBuild children were stopped. A bounded single-node retry exposed and repaired a test DTO compile mismatch. Final worker local outcome: 29 passed, 10 PostgreSQL skips.

Coordinator focused container rerun at `4763ada`, image `sha256:ac22b8129e3f0a520b710034e8d5ae82c33462dc0b96676c38ea956708959224`, passed **Procurement 39/39**, **Sandbox 2/2**, **WireMock 2/2**, with **zero failures or skips**. Exact TRX files are in `artifacts/procurement-lab/focused-final-results/`. This confirms PROC-04, PROC-07 and PROC-08 repairs against real PostgreSQL. Unaffected full-regression suites are retained from the preceding run; these results are not described as one newly rerun complete suite.

Actual R08 passed with the same verified Kafka container stopped and restarted. Receipt `35f101df-2b11-4328-991d-e9ee75f63a90` committed while Kafka was stopped; Inventory stayed at 30; source/durable transport evidence persisted; after recovery Inventory reached 33 and matching receipt replay left it at 33. `artifacts/procurement-lab/broker-recovery.json` preserves both database observations and the finally-recovery result. Actual `DENY-001` submission/replay returned stable Rejected and receipt attempt 409 with no stock change (`denied-order.json`).

Supplier repair `ac0c4b3` (integrated `4763ada`) fixed named parameter examples and unmatched dispatch default, used bounded supplier responses with Content-Length to avoid the observed Microcks duplicated chunked-transfer headers, and serialized native mapping resets. The root deleted only this workflow's initial Microcks service after exporting its failed import state; the next imports used a stable `supplier-api.yaml` source identity. Repaired startup passed, and **all 17 HTTP scenarios passed** in `http-contracts-repaired.json`. Microcks native UI visibly exposed the three operations and the actual PROXY_FALLBACK rule editor.

Final read-only support review by the GPT-6 Sol worker identified remaining supplier-control issues inherited from the initial delivery: enum parsing accepted numeric mode strings; interrupted delete/rebuild could leave partial mappings while claiming the old mode; fixed order matching omitted quantity/price/currency. The parent confirmed these concerns and assigned bounded repairs to Luna, including an explicit non-ready state and complete fixture matching. These review contributions are attributed support; parent retains review ownership.

Actual browser U03 against `4763ada` found `SyntaxError: Unexpected token '}'` in the sandbox inline script and `ReferenceError: saveDelay is not defined` when Apply was clicked. The UI rendered but its controls/journals were not functional. Luna reproduced the extra closing brace using extracted-script `node --check`; repair and browser recheck are active. A passing C# build did not validate inline JavaScript.

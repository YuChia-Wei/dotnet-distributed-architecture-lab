# Frontend acceptance and model observation report

created_at: 2026-09-26T07:03:15+00:00; updated_at: 2026-09-26T07:03:15+00:00

Status: implementation acceptance completed. All 17 selected implementation scenarios have their required evidence. D01 remains a separately authorized provider lifecycle operation; no prospective PR, merge or cleanup pass is claimed.

## Selection and independent stages

- One workflow2026-09-26-commerce-frontend, Issue18; authorized frontend scope and owner clarification internal sales/warehouse users. Requirements/architecture/specifications/test-specification are selected ordinary Markdown with the original v1 retained. No CBF machine format selected; structural CBF validation is not applicable.
- Plan/review/assess uses current spec-compliance-validator instructions, explicit dotnet@0.1.0 profile only for SupplierMock/Product, plus project-selected frontend GWT/runtime obligations. Retained compliance packet digest0b2dfd7cc6ea3ea57ce4ae942fb8191c85428597764a5e44eb10a1dbe6c1efb5. Generic Vue review uses accepted explicit API/UI contracts, not unadopted .NET conventions.
- Root coordinator independently reviewed Sol code, real database/broker/browser observations; self-authored specifications are self-review, not independent source authority. Review findings and first failures remain in review-notes.
- Structure: workflow public checkpoint/inspect validates owned record only. Authoring: owner-authorized scope, source-backed API inventory. Semantics: Inventory restock and required Product description corrected against domain source. Runtime: matrix below, no unit result upgraded to actual external acceptance.

## Complete selected GWT inventory

Each row selects its entire Given/When/Then from test-specification.md, including independent clauses. Input/error/concurrency clauses in specifications.md are mapped in the following contract matrix. D01 is provider-only and does not become a prospective implementation pass.

| ID / AC | Actual evidence and assertion | Current result |
| --- | --- | --- |
| W01 / AC07 | Browser product search showed1/7, actual19.99 detail; no fabricated pagination/stock. | satisfied |
| W02 / AC07 | Real UI single-product qty2 order01a0dc75-2757-73d2-b837-0c08a755653b; queried lineItems match; Inventory12->10 through actual broker reservation. sales-stock-readback.json | satisfied |
| W03 / AC07 | Sol Web node/DOM suite10passes at worker1f008; async errors, malformed response, quantity, money and mutation uncertainty cases. Later Nginx-only change leaves test/code content unchanged. | satisfied at component level |
| W04 / AC07 | Known order deep-route reload renders actual lineItems; unknown00000000-0000-4000-8000-000000000018 gives error+retry and no invented details. Browser-local history visibly labeled. | satisfied |
| A01 / AC02 | Admin create/edit persisted retained product01a0dc6d-d43e-7fee-91c8-37c01885913b. Disposable product01a0dc7a-e438-743d-aef9-8f43aca795f2 created then delete cancellation/Escape preserved row; confirmed soft-delete refreshed list7. | satisfied |
| A02 / AC07 | Actual missing stock returned error; explicit initialization10, increase3->13, decrease2->11, additive restock1->12. | satisfied |
| A03 / AC07 | Purchase2fc0f818-df61-470d-8057-53f257057ee1 direct REAL-001 qty4 accepted, received0 and stock10 unchanged; purchase-before-receipt.json | satisfied |
| A04 / AC07 | UI delay10000, purchase46868f7c-c1c6-429c-9528-2640d7955da7 showed SubmissionUnknown. UI reconcile same key6f0a8f0d-f2db-4575-8776-66199165b595 ->Accepted. Native log exactly onePOST+oneGET; stock14 unchanged; delay restored0. delayed-reconciliation.json | satisfied |
| A05 / AC07 | Receive2 then2: partial/final states and two actual receipts; stock10->12->14. Qty3 whenremaining2 disabled. FinalReceived disables receipt. Ambiguous/same-ID and route race validated by Web component tests. first-receipt-stock.json,purchase-after-receipts.json | satisfied at declared levels |
| M01 / AC03 | UI switched mock/proxy/hybrid with confirmation. Native mock MOCK-001 originwiremock, REAL-001404; proxyREAL-001originsandbox; hybridbothorigins. UI log2 then confirmedclear0. wiremock-*.json | satisfied |
| M02 / AC03 | Actual initial imports failed and remained truthfully unconfirmed. Native 1.15 request contract repaired and deployed. UI selected mock, proxy, hybrid; live dispatcher readback matched all three. Mock MOCK-001 origin microcks and REAL-001 unmatched400; proxy REAL-001 origin sandbox; hybrid mock/proxy origins and exact fixed POST origin microcks confirmed. microcks-*-final.json. In-memory cases cover invalidmode/noI/O, unconfigured/custom, malformedJSON, failures, pagination and readback. | satisfied |
| M03 / AC03 | UI displayed real33orders/52requests, input10001 browser range-invalid, valid10000 readback and restored0. Final initial-load/readback race repair passed 19 Admin DOM tests; deployed UI set1 and restored0, each matched native readback. | satisfied |
| R01 / AC04 | Production Nginx viaYARP bareprefixes follow relative redirects to correct8888origin; roots and deep URLs200, browser refresh usable. routing-matrix.json | satisfied |
| R02 / AC04 | Missing js/ico/jpg and unknownAPI404, ProductsJSON200; noSPA200 for missing selected assets/API. routing-matrix.json | satisfied |
| Q01 / AC05 | Desktop and390px Web purchase, Admin overview/product; document375px within390viewport, no horizontalpageoverflow. Tab fromname todescription, visiblefocus and dialogEscape/cancel tested; tables contained. | satisfied within inspected views |
| Q02 / AC05 | Live missingInventory/unknownOrder and Microcks failure showerrors/retry while othernavigationworks; staleGET/receipt guards coveredbycomponenttests. | satisfied |
| Q03 / AC05 |9protectedcontainers captured IDs/starttimes/status/mounttype+source+destination identical. Existing PostgreSQL/broker data and priorfixtures retained; no down/prune/volumedeletion. protected-comparison.json | satisfied at integration snapshot |
| D01 / AC06 | PR/merge/main readback, durable C deployment and onlytaskcleanup follow reviewed implementation head. Owner authorized directly. | provider lifecycle pending |

## Contract-level coverage and limits

| Specification obligation | Evidence / applicable boundary |
| --- | --- |
| Same-origin API, valid request/response fields, empty successfulPUT/DELETE | Exactapi/contracts sources plus livebrowser CRUD/order/Inventory/Procurement/control above. |
| Required product name+description, money finite/nonnegative/two decimals; quantity andstockint32 | Guardcode, Solunit/DOM cases; actual19.99 and newlydeployed blank-description inlineerror focus. Descriptionmissing was bothbaselineomission and implementationgap, now corrected. |
| No automaticmutationretry; immutablepurchase/receiptidentity; uncertain body/transport result | Web componenttests and real delayedpurchase onePOST proof. Serverexactlyonce forOrders is explicitly not promised. |
| Readiness/unknown/custom/upstreamfailure; fixedorigin/fixedpresets and escapedJSON | Adaptertests/parsercode; actual failedmode displayedunconfirmed. M02 includes final native verification. |
| Default unchanged, duplicatebusyguard, explicit destructiveconfirmation | SourceandDOM tests; actualEscape/cancel/delete/modes. M03 includes final initial-load and immutable readback coverage. |
| Build/runtime routing and Dockerprotection | ActualNode22Docker builds/typechecks and nginx-t; nativeDocker routes and preservedcontainerbaseline. |
| Baselineexistingdomaincontracts | Existing Products/Orders Dapper, InventoryEF and messaging remain. OnlyorphanSQL removed, confirmed against schema+domain and actualPostgres CRUD. No claim of fullbackend regression or unrelatedretired analyzers. |

## Reproduction and evidence retention

Working root F:/git-worktree/commerce-frontend/dotnet-mq-arch-lab. Raw evidence artifacts/frontend-lab is ignored; copy to durable C:/Github/YuChia/dotnet-mq-arch-lab/artifacts/frontend-lab before archival. Exact source and evidence hashes are retained in acceptance-evidence.json; post-merge deployment receives a separate local provider receipt. Commands use five Compose files documented in commerce-frontend.md; F-only temporary sixth override stages gateway configuration on C due Docker Desktop RAMdisk bind failure.

Frontend runner is Vitest5/node22 with DOMfixtures; .NET is repository-pinned SDK10/xUnitv3. Worker exactcommands: npm run test, npm run build (includesvue-tsc), npm audit; Microcks filtered dotnet test tests/SupplierMock.Tests/SupplierMock.Tests.csproj -c Release --no-restore --filter FullyQualifiedName~MicrocksPresetTests. Parent did not rerun old listener suites after owner networkprompt instruction. Root extraWebtest attempt lacked installedVitest; npmci download was rejected by automaticapprovalreview. No dependency-install workaround or permissiondialog selfapproval occurred. Existing worker evidence is attributed and separate from actualDocker acceptance.

## Model observation

GPT-6 Sol/high implemented the Web, Admin and platform partitions in separateownedworktrees. Root gpt-6-astra/ultra supplied specifications, integrated and reviewed. Initial implementations needed boundedrepairs for asyncidentity, floatingmoney, nullablemetadata, Docker/Nginx configuration, Product description, Sandboxrace, and nativeMicrocks protocol. Sol also identified an error in the parent's restockspecification and cross-review found Sandbox defects. This supports using Sol with concretecontracts and review; it is not a comparative benchmark. Luna was not used in this frontend workflow. Actualtoken/cost totals unavailable; task scopes differ, so no ranking orcost claim.

## Final subject and scoped conclusion

The implementation subject is `1e8fca81b2e1fc6602dec5d1ddf706f5a701938d`. Final worker subjects: Web `dcb93ca4ae0b10e0c6cc5df2419aa7a442fd2bd8` (Nginx only after 10 tests), Admin `f36f3ea1b57b0e9e1191fe644b2c6488b68ee972` (19 tests), platform `97b760fdc8b251356aa2ce303896ad25077080cf` (9 in-memory tests, no restore). Their exact product payloads were integrated and the affected Docker/browser checks repeated. Later documentation and workflow-record commits do not change these tested product bytes. All selected implementation criteria are satisfied at their declared levels: **compliant-within-scope**; no full-repository, production-security, performance or independent framework-admission claim.

Provider lifecycle D01 is deferred only until the reviewed commit is published, under direct owner authorization and WORKFLOW-ARTIFACT-POLICY's provider-only completion boundary. It is owned by the same root coordinator and remains in this single workflow's delivery sequence. No evidence-sync commit will fabricate a future outcome.

Automatic approval review blocked the optional root dependency reinstall (`npm ci`) because it would download over the network after the owner requested deferring permission-prompt tests. The prior root test attempt lacked Vitest. Both remain unsuccessful attempts; worker results above came from their existing installed dependencies, and actual acceptance used the existing Docker services.

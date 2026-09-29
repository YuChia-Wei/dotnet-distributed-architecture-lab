# Procurement and supplier mock/proxy laboratory

## Workflow metadata
- workflow_id: `2026-09-26-procurement-supplier-lab`
- owner_skill: `software-development-orchestrator`
- branch: `codex/2026-09-26-procurement-supplier-lab`; base_branch: `main`
- status: `completed` (v2 revision 14; completion applies to workflow-owned tasks only)
- created_at: `2026-09-26T10:47:32+08:00` (locator); original v2 record created_at: `2026-09-26T02:44:16.013339+00:00`
- updated_at: `2026-09-29T22:11:55+08:00` (migration); original v2 record updated_at: `2026-09-26T04:15:16.970345+00:00`
- source: [exact v2 JSON](evidence/v2-source.workflow.json), SHA-256 `fe4a21c4469d3c5f6756a69fa2e6424d2d44a2deb661ab5150f83d805f530622`
- stable ID map and complete history: [migration-map.md](migration-map.md)

## Scope and intent

Deliver one owner-reviewable procurement and supplier integration laboratory, including native mock/proxy behavior, controls, specifications, actual validation and attributed GPT-6 Sol/Luna implementation.

**Included:**
- Procurement purchase and receipt lifecycle
- SupplierSandbox.WebApi actual upstream
- Inventory idempotent goods receipt
- Microcks and WireMock.Net native mock/proxy controls
- Requirements, specifications, verification and model evidence in one workflow

**Excluded:**
- Payments
- Production deployment or credentials
- Main merge, push, release and Issue closure before owner review

## Development stages

| Task | Work | Depends on | State | Record |
| --- | --- | --- | --- | --- |
| `T001` | Author the bounded requirements, architecture and executable API/test contracts for Issue 17. | none | `completed` | [task](tasks/T001.json) |
| `T002` | Supplier and native mocks | T001 | `completed` | [task](tasks/T002.json) |
| `T003` | Procurement lifecycle | T001 | `completed` | [task](tasks/T003.json) |
| `T004` | Inventory receiving | T001 | `completed` | [task](tasks/T004.json) |
| `T005` | Integrated lab operation | T001 | `completed` | [task](tasks/T005.json) |
| `T006` | Acceptance and parent review | T002, T003, T004, T005 | `completed` | [task](tasks/T006.json) |

## Acceptance

| ID | Criterion | Disposition | Evidence IDs | Reason or condition |
| --- | --- | --- | --- | --- |
| `AC01` | Purchase submission and supplier order idempotency/reconciliation follow the documented contract. | `succeeded` | EV-FINAL-HTTP, EV-FINAL-COMPLIANCE | Parent assessment within the explicit selected specification; exact observations and limits retained in acceptance-report.md. |
| `AC02` | Physical partial receipts commit once and are eventually applied once in Inventory. | `succeeded` | EV-FINAL-COMPLIANCE | Parent assessment within the explicit selected specification; exact observations and limits retained in acceptance-report.md. |
| `AC03` | Both mock platforms demonstrate native mock hits and upstream proxy forwarding with provenance. | `succeeded` | EV-FINAL-HTTP | Parent assessment within the explicit selected specification; exact observations and limits retained in acceptance-report.md. |
| `AC04` | Local management UI and configuration instructions make modes and requests observable. | `succeeded` | EV-FINAL-UI | Parent assessment within the explicit selected specification; exact observations and limits retained in acceptance-report.md. |
| `AC05` | Requirements and complete behavior/API/test specifications map to actual tests and runtime evidence. | `succeeded` | EV-FINAL-COMPLIANCE | Parent assessment within the explicit selected specification; exact observations and limits retained in acceptance-report.md. |
| `AC06` | Sol/Luna implementation evidence and parent review are retained without unsupported comparative claims. | `succeeded` | EV-FINAL-COMPLIANCE | Parent assessment within the explicit selected specification; exact observations and limits retained in acceptance-report.md. |

## Decisions

- No decision entry in the v2 record.

## Evidence and references

| Evidence ID | Task | Disposition | Subject and source |
| --- | --- | --- | --- |
| `EV-SPEC-01` | T001 | `succeeded` | requirements.md, architecture.md, specifications.md, test-specification.md version 1; refs: SPEC-BASELINE |
| `EV-FIRST-PG-FAIL` | T003 | `failed` | Procurement source/tests 79437e8; parent build subject c757dfd; mqarchlab-procurement-first-delivery-tests:17; PostgreSQL16.15; refs: FIRST-PG-TRX |
| `EV-FIRST-HTTP` | T005 | `failed` | abeedde Supplier; 4375495 deployed Procurement; c2e098c runner; refs: FIRST-HTTP |
| `EV-DIRECT-FLOW` | T005 | `succeeded` | 4375495 deployed Procurement and f4befe9 Inventory; refs: DIRECT-FLOW |
| `EV-T003-PG` | T003 | `succeeded` | 0946879 Procurement source/tests; refs: FINAL-PROC-TRX |
| `EV-T004-PG-BROKER` | T004 | `succeeded` | f4befe9 Inventory and deployedfirst Procurement4375495; refs: INVENTORY-TRX, BROKER-RECOVERY, DIRECT-FLOW |
| `EV-HTTP-REPAIRED` | T005 | `succeeded` | 4763ada supplier and0946879 procurement; refs: REPAIRED-HTTP |
| `EV-FINAL-SUPPLIER` | workflow | `succeeded` | Product runtime source35589b8; reused Procurement/Inventory/R08 subjects explicitly identified in acceptance-report.md.; refs: FINAL-TESTS |
| `EV-FINAL-HTTP` | workflow | `succeeded` | Product runtime source35589b8; reused Procurement/Inventory/R08 subjects explicitly identified in acceptance-report.md.; refs: FINAL-HTTP, FINAL-SUPPLEMENTAL |
| `EV-FINAL-UI` | workflow | `succeeded` | Product runtime source35589b8; reused Procurement/Inventory/R08 subjects explicitly identified in acceptance-report.md.; refs: FINAL-BROWSER |
| `EV-FINAL-PROTECTED` | workflow | `succeeded` | Product runtime source35589b8; reused Procurement/Inventory/R08 subjects explicitly identified in acceptance-report.md.; refs: FINAL-PROTECTED |
| `EV-LEGACY-LOCATOR-LIMIT` | workflow | `failed` | Product runtime source35589b8; reused Procurement/Inventory/R08 subjects explicitly identified in acceptance-report.md.; refs: LEGACY-LOCATOR-LIMIT |
| `EV-FINAL-COMPLIANCE` | workflow | `succeeded` | Product runtime source35589b8; reused Procurement/Inventory/R08 subjects explicitly identified in acceptance-report.md.; refs: FINAL-ACCEPTANCE, FINAL-MODEL-REVIEW, FINAL-EVIDENCE-MANIFEST, FINAL-FRAMEWORK-CHECK |

Reference IDs, targets, resolution and digests are preserved without shortening in [migration-map.md](migration-map.md) and the exact source JSON.

## Current progress and continuation

Owner review and any push, PR, merge, Issue closure or release remain separate from this completed local workflow record.

The original `completed` state does not establish every check, provider action, integration or cleanup as completed. Earlier failures and their later corrections remain in the original history and the existing review/acceptance reports.

Review and acceptance: [review-and-model-observations.md](review-and-model-observations.md), [acceptance-report.md](acceptance-report.md).

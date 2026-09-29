# Commerce internal operations and administration frontends

## Workflow metadata
- workflow_id: `2026-09-26-commerce-frontend`
- owner_skill: `software-development-orchestrator`
- branch: `codex/2026-09-26-commerce-frontend`; base_branch: `main`
- status: `completed` (v2 revision 9; completion applies to workflow-owned tasks only)
- created_at: `2026-09-26T14:14:39+08:00` (locator); original v2 record created_at: `2026-09-26T06:11:01.468147+00:00`
- updated_at: `2026-09-29T22:11:55+08:00` (migration); original v2 record updated_at: `2026-09-26T07:08:47.511016+00:00`
- source: [exact v2 JSON](evidence/v2-source.workflow.json), SHA-256 `1212750ced64a2cc08020b324e9448270703138801bb53fce1193a0e3886833c`
- stable ID map and complete history: [migration-map.md](migration-map.md)

## Scope and intent

Deliver Vue3 TypeScript internal sales/warehouse operations and administration applications under src through Nginx and one YARP gateway, with GPT-6 Sol implementation and coordinator review. Issue18; provider PR/merge/cleanup separately verified under direct owner authorization.

**Included:**
- Internal sales/warehouse operations: products sales orders Inventory Procurement and receiving
- Administration: product master maintenance service status and mock/proxy controls
- Nginx YARP routing production deployment and real browser acceptance
- One coordinated workflow with Sol implementation and parent review
- Minimal existing Product repository repair needed for real administration update: remove obsolete productsales delete; keep Dapper and current schema

**Excluded:**
- Production identity tenant isolation payment
- Unrelated framework authority changes
- Changes to protected observability deployment

## Development stages

| Task | Work | Depends on | State | Record |
| --- | --- | --- | --- | --- |
| `T001` | Define requirements architecture UI/API contracts and observable scenarios | none | `completed` | [task](tasks/T001.json) |
| `T002` | Internal operations web | T001 | `completed` | [task](tasks/T002.json) |
| `T003` | Administration web | T001 | `completed` | [task](tasks/T003.json) |
| `T004` | Gateway and mock management adapter | T001 | `completed` | [task](tasks/T004.json) |
| `T005` | Integrated acceptance and review | T002, T003, T004 | `completed` | [task](tasks/T005.json) |

## Acceptance

| ID | Criterion | Disposition | Evidence IDs | Reason or condition |
| --- | --- | --- | --- | --- |
| `AC01` | Real responsive customer workflows and honest states | `not-applicable` | none | Owner clarified ordinary users are internal sales/warehouse staff; replaced by AC07 before code implementation. |
| `AC02` | Real administration domain operations and safe request identity | `succeeded` | EV-T005-FINAL | All applicable implementation criteria mapped to actual or explicitly declared component evidence in final report. |
| `AC03` | Integrated WireMock.Net and Microcks controls with documented boundaries | `succeeded` | EV-T005-FINAL | All applicable implementation criteria mapped to actual or explicitly declared component evidence in final report. |
| `AC04` | Nginx production builds and same-origin YARP subpath routing | `succeeded` | EV-T005-FINAL | All applicable implementation criteria mapped to actual or explicitly declared component evidence in final report. |
| `AC05` | Specifications actual browser/gateway validation and protected Docker preservation | `succeeded` | EV-T005-FINAL | All applicable implementation criteria mapped to actual or explicitly declared component evidence in final report. |
| `AC06` | Reviewed PR merged to main and task branches/worktrees cleaned | `deferred` | none | Provider-only delivery follows the reviewed implementation commit within the same workflow sequence. Deferral: {"authority_ref":"Direct user frontend request authorizes Issue, PR, merge and cleanup; .dev/standards/WORKFLOW-ARTIFACT-POLICY.md Workflow Completion","next_action":"Create PR, merge with merge commit, verify remote main, deploy from primary C checkout, close Issue18 and archive only current task worktrees/branches.","owner":"root coordinator","reason":"Implementation completion precedes provider-only PR/merge/main readback and cleanup; target policy prohibits prospective pass or evidence-sync commit.","trigger":"Reviewed implementation commit finalized and pushed"} |
| `AC07` | Real responsive internal operations frontend supports products sales-order lookup/creation Inventory and Procurement receiving with honest states | `succeeded` | EV-T005-FINAL | All applicable implementation criteria mapped to actual or explicitly declared component evidence in final report. |

## Decisions

- `D-AUDIENCE` `resolved` — Who are ordinary frontend users? Resolution: Internal sales/warehouse staff; /web owns stock procurement receiving and sales operations, /admin owns master maintenance and developer tools. Owner: user.

## Evidence and references

| Evidence ID | Task | Disposition | Subject and source |
| --- | --- | --- | --- |
| `EV-SPEC18` | T001 | `succeeded` | Frontend requirements architecture API/UI contracts and GWT baseline v1; refs: SPEC18 |
| `EV-T002` | T002 | `succeeded` | Worker implementation ending at 1f008044f101beb8842200f3c6a0099eb731c8c6; refs: IMPL-T002 |
| `EV-T003` | T003 | `succeeded` | Worker implementation ending at c89da4b06548ee8a43eac61538cd11b7c826a246; refs: IMPL-T003 |
| `EV-T004` | T004 | `succeeded` | Worker implementation ending at 8ed57760de3e43bf01f0223a8695e2da8647dba9; refs: IMPL-T004 |
| `EV-T005-FAILURES` | T005 | `failed` | Historical integrated attempts before final implementation 1e8fca81b2e1fc6602dec5d1ddf706f5a701938d; refs: REVIEW-FINAL |
| `EV-T005-FINAL` | T005 | `succeeded` | Final product bytes at 1e8fca81b2e1fc6602dec5d1ddf706f5a701938d; exact manifest and scoped acceptance report; refs: ACCEPTANCE-FINAL, MANIFEST-FINAL, REVIEW-FINAL, SPEC18-FINAL |

Reference IDs, targets, resolution and digests are preserved without shortening in [migration-map.md](migration-map.md) and the exact source JSON.

## Current progress and continuation

AC06 remains deferred: reviewed implementation head, PR/merge/main read-back, durable C: deployment and task-worktree cleanup require their stated provider lifecycle conditions.

The original `completed` state does not establish every check, provider action, integration or cleanup as completed. Earlier failures and their later corrections remain in the original history and the existing review/acceptance reports.

Review and acceptance: [review-notes.md](review-notes.md), [acceptance-report.md](acceptance-report.md).

# Critical Remediation And Analyzer Integration Plan

## Template Metadata

- `template_id`: `dev-workflow/development-workflow-plan`
- `template_version`: `1.1.0`
- `template_created_at`: `2026-07-10T18:25:11+08:00`
- `template_updated_at`: `2026-07-11T00:22:30+08:00`

## Workflow Metadata

- `workflow_id`: `2026-07-13-critical-remediation-and-analyzer-integration`
- `plan_id`: `development-plan-2026-07-13-critical-remediation-and-analyzer-integration`
- `owner_skill`: `dev-workflow`
- `branch`: `codex/2026-07-13-critical-remediation-and-analyzer-integration`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `active`
- `created_at`: `2026-07-13T22:37:26+08:00`
- `updated_at`: `2026-07-13T23:40:00+08:00`
- `template_source`: `.ai/assets/skills/dev-workflow/templates/development-workflow-plan-template.md`
- `template_version`: `1.1.0`
- `workflow_locator`: `.dev/workflows/2026-07-13-critical-remediation-and-analyzer-integration/workflow.yaml`
- `artifact_root`: `.dev/workflows/2026-07-13-critical-remediation-and-analyzer-integration/`

## Development Objective

- Product or software outcome: Persist the repository assessment, make every CRITICAL and MUST FIX finding durably discoverable, integrate the source-included Roslyn analyzers into product builds, then remediate the critical architecture and reliability gaps through bounded reviewed slices.
- Current lifecycle entry point: Existing implementation plus a completed conversational code review; start at review persistence, architecture direction, and a bounded tooling integration slice.
- User constraints: Inspect and terminate only stale repository test processes; preserve Rider processes; use workflow mode; keep scheduled CRITICAL/MUST FIX detail in workflow tasks; use Wolverine PostgreSQL first behind a replaceable port; support Kafka and RabbitMQ; use memory queues for required automated tests; run external-broker suites only when explicitly requested.
- Non-goals: Do not kill Rider-owned processes; do not conceal existing analyzer violations; do not combine all architecture remediations into one unreviewable change; do not claim production readiness without end-to-end messaging tests.

## Inputs

- Requirements: `.dev/requirement/distributed-commerce-bounded-context-overview.md`
- Specifications: `.dev/specs/`, `.dev/problem-frames/orders/cbf/place-order/`
- Architecture decisions: `.dev/ARCHITECTURE.md`, `.dev/operations/context-map.md`, `.dev/operations/event-catalog.md`, `.dev/operations/mq-topology.md`
- Existing implementation or tests: `src/`, `tests/`, `tools/DotnetBackendAnalyzers/`, `tools/DotnetBackendValidation/`

## Skill Routing

| Capability slot | Owner skill | Confidence | Evidence |
| --- | --- | --- | --- |
| Workflow orchestration | `dev-workflow` | high | Active capability profile mapping |
| Architecture | `ddd-ca-hex-architect` | high | Active capability profile mapping |
| Test design | `bdd-gwt-test-designer` | high | Active capability profile mapping |
| Implementation | `slice-implementer` | high | Active capability profile mapping |
| Review | `code-reviewer` | high | Active capability profile mapping |
| Compliance validation | `spec-compliance-validator` | high | Active capability profile mapping; applies when a problem frame governs the slice |

## Development Stages

### Stage 1 — Persist Review And Backlog

- `stage_id`: `assessment-and-backlog`
- Goal: Land the scored review with evidence and register every CRITICAL and MUST FIX finding as a durable backlog item.
- Capability slot: `workflow-orchestration`, `review`
- Owner skill: `dev-workflow` with existing `code-reviewer` output
- Scope: Workflow review report, backlog items, indexes, traceability links.
- Non-goals: No product remediation in this stage.
- Dependencies: Completed conversational assessment and current repository evidence.
- Validation: YAML/JSON parse, workflow artifact validator, link/reference review.
- Commit checkpoint: `DEV-001` after validation.
- Historical note: This checkpoint initially created durable backlog items. After the user confirmed one workflow should execute the scheduled work, their evidence and acceptance criteria were migrated into the workflow tasks. Only deferred Product commercial work remains in the durable backlog.

### Stage 2 — Integrate Source-Included Analyzers

- `stage_id`: `analyzer-integration`
- Goal: Make `DotnetBackendAnalyzers` execute during normal production builds without adding a runtime assembly dependency.
- Capability slot: `implementation`
- Owner skill: `slice-implementer` using generic remediation mode
- Scope: Shared build configuration for `src/`, analyzer severity policy if needed, documentation and validation.
- Non-goals: Do not fix unrelated analyzer findings in the same slice.
- Dependencies: Analyzer project and its tests must build independently.
- Validation: Analyzer tests, product build proving analyzer load, intentional diagnostic inventory.
- Commit checkpoint: `DEV-002` after validation.

### Stage 3 — Approve Critical Architecture Direction

- `stage_id`: `critical-architecture-direction`
- Goal: Define the bounded target decisions for ES persistence lifecycle, legal order transitions, durable messaging, and repository CQRS separation.
- Capability slot: `architecture`
- Owner skill: `ddd-ca-hex-architect`
- Scope: Decisions, tradeoffs, dependency boundaries, task refinements and non-goals.
- Non-goals: No broad implementation before the decisions are recorded.
- Dependencies: `DEV-001`, analyzer diagnostic inventory from `DEV-002`.
- Validation: Decision-to-finding traceability and affected contract review.
- Commit checkpoint: `DEV-003` after validation.

### Stage 4 — Remediate Critical Domain And Persistence Findings

- `stage_id`: `critical-domain-remediation`
- Goal: Correct aggregate version/pending-event lifecycle and legal order-state transitions with focused tests.
- Capability slot: `implementation`, `test-design`
- Owner skill: `slice-implementer` with `bdd-gwt-test-designer`
- Scope: One bounded ES persistence slice and one bounded Order state-machine slice.
- Non-goals: No unrelated repository or broker refactor.
- Dependencies: `DEV-003`.
- Validation: Narrow domain/infrastructure tests, analyzer-enabled build, relevant problem-frame compliance when applicable.
- Commit checkpoint: `DEV-004`, split into coherent commits if the two slices validate independently.

### Stage 5 — Remediate Messaging And CQRS Findings

- `stage_id`: `messaging-and-cqrs-remediation`
- Goal: Establish durable publish boundaries, command/query repository separation, broker topology completeness, publisher activation, idempotency and failure policy.
- Capability slot: `architecture`, `implementation`, `test-design`
- Owner skill: `ddd-ca-hex-architect`, then `slice-implementer` and `bdd-gwt-test-designer`
- Scope: `DEV-005` durable ports/Wolverine PostgreSQL adapter; `DEV-010` CQRS repositories; `DEV-011` Kafka/RabbitMQ parity and configuration; `DEV-012` reservation idempotency/failure policy.
- Non-goals: Product producer work; no external-broker dependency in default automated tests; no production claim without matching evidence.
- Dependencies: `DEV-003`, `DEV-004` where event lifecycle is shared.
- Validation: Analyzer-enabled build, memory-transport contract/routing tests, topology/config checks, review; real broker connectivity only through explicit manual commands.
- Commit checkpoint: One checkpoint per DEV-005/010/011/012 bounded slice.

### Stage 6 — Restore Test Reliability And Coverage

- `stage_id`: `test-remediation`
- Goal: Make tests reproducible, align them with GWT/NSubstitute/event-observation rules, and close high-risk coverage gaps beginning with Inventory and PlaceOrder.
- Capability slot: `test-design`, `implementation`
- Owner skill: `bdd-gwt-test-designer`, then `slice-implementer`
- Scope: Test host isolation, dependency reproducibility, critical behavior coverage.
- Non-goals: Do not chase a numeric coverage target without behavior traceability.
- Dependencies: Stable contracts from preceding remediation slices.
- Validation: Full solution tests plus narrow broker/infrastructure suites without leaked processes.
- Commit checkpoint: `DEV-006` after each coherent test batch.

### Stage 7 — Final Review And Closure

- `stage_id`: `review-and-close`
- Goal: Re-score the repository, verify backlog/workflow states and close only after required gates pass.
- Capability slot: `review`, `compliance-validation`
- Owner skill: `code-reviewer`; `spec-compliance-validator` for governed problem-frame slices
- Scope: Final findings, validation evidence, backlog resolution links, commit and merge readiness.
- Non-goals: No new remediation hidden inside final review.
- Dependencies: All scheduled critical and MUST FIX tasks completed or explicitly deferred with user-approved reason.
- Validation: Full solution build/tests, analyzer tests, runtime validation tests, quick repository gate, workflow validator.
- Commit checkpoint: `DEV-007` final workflow commit.

## Validation Strategy

- Requirement/spec traceability: Every backlog item links the review evidence and any governing requirement/spec/problem frame.
- Architecture validation: `ddd-ca-hex-architect` owns direction; `code-reviewer` independently verifies implemented boundaries.
- Test and implementation validation: Prefer narrow tests first, then analyzer-enabled `dotnet build MQArchLab.slnx`, full tests, and broker-specific integration checks.
- Review/compliance gates: Problem-frame work requires `spec-compliance-validator` at 100%; other work requires checklist review and recorded residual risk.

## Progress And Handoff

- Current stage: `critical-domain-remediation` (`DEV-004`).
- Completed stages: `assessment-and-backlog` (`DEV-001`); `analyzer-integration` (`DEV-002`); `critical-architecture-direction` (`DEV-003`).
- Deferred stages and reasons: Product integration producer (`MSG-003`) is deferred until a future commercial requirement approves event meaning and consumer need.
- Open decisions: DEV-005 must verify whether Wolverine PostgreSQL envelope persistence can enlist in the existing Dapper/Npgsql transaction. If it cannot, use a native transactional outbox adapter and keep Wolverine as the delivery runtime.
- Continuation instructions: Finish DEV-004 repository failure/concurrency coverage and validation, then execute DEV-005 before the independent MUST FIX slices.
- Analyzer-discovered follow-ups: `DEV-008` migrates staged Use Case/Handler diagnostics; `DEV-009` removes the confirmed high-severity OpenAPI dependency vulnerability.
- Branch history and checkpoint handoffs: Segment 1 started from local `main`; no push or merge requested yet.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-07-13-critical-remediation-and-analyzer-integration` | `main` | active | `fd80fb7` | local | `2026-07-13T22:53:58+08:00` | DEV-001 and DEV-002 checkpoints complete | Continue with DEV-003 on current branch |

## Completion Summary

- Outcome: Active.
- Changed artifacts: Workflow locator, plan, tasks, review report, backlog, analyzer integration.
- Validation evidence: Workflow validator passed; analyzer-enabled product build passed; analyzer tests 47/47 and runtime validation tests 2/2 passed; quick gate passed 7/7; no analyzer runtime dependency was found.
- Commits: `42d8e49` workflow bootstrap; `dab7e17` assessment/backlog; `fd80fb7` analyzer integration.
- Residual risks: DEV-004 infrastructure tests remain; Wolverine/Dapper atomic enlistment is not yet proven; remaining MUST FIX tasks are pending.

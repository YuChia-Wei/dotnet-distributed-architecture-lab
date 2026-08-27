# Reconstructable System Specification Plan

## Template Metadata

- `template_id`: `software-development-orchestrator/development-workflow-plan`
- `template_version`: `1.4.0`
- `template_created_at`: `2026-07-10T18:25:11+08:00`
- `template_updated_at`: `2026-08-05T02:12:00+08:00`

## Workflow Metadata

- `workflow_id`: `2026-08-26-reconstructable-system-specification`
- `plan_id`: `development-plan-2026-08-26-reconstructable-system-specification`
- `owner_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-08-26-reconstructable-system-specification`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `active`
- `created_at`: `2026-08-26T19:03:36+08:00`
- `updated_at`: `2026-08-27T08:53:12+08:00`
- `template_source`: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `template_version`: `1.4.0`
- `workflow_locator`: `.dev/workflows/2026-08-26-reconstructable-system-specification/workflow.yaml`
- `artifact_root`: `.dev/workflows/2026-08-26-reconstructable-system-specification/`
- `work_item`: `GitHub Issue #2`

## Development Objective

- Product or software outcome: Create a repository-native specification baseline from which a low-reasoning-cost AI model can reconstruct the current distributed commerce system without relying on product source code or hidden conversation context.
- Current lifecycle entry point: Reverse engineering and specification authoring from the current repository implementation, tests, configuration, and retained documents.
- User constraints: Preserve or improve current quality; make the documentation sufficient after all product source code is removed; optimize clarity for a LUNA-class model.
- Non-goals: Delete source code; implement RabbitMQ fanout/dual deployment; convert every Inventory command to outbox; push; create a pull request; merge; close Issue #2; publish or release.

## Inputs

- Requirements: Existing `.dev/requirement/` documents and the user-authorized reconstruction objective.
- Specifications: Existing `.dev/specs/`, `.dev/problem-frames/`, tests, and implementation evidence.
- Architecture decisions: `.dev/ARCHITECTURE.md`, retained ADRs, solution/project files, Docker Compose topology, and runtime configuration.
- Existing implementation or tests: `src/`, `tests/`, `MQArchLab.slnx`, `*.csproj`, SQL, appsettings, and Dockerfiles.

## Development Stages

### RECON-001 — Evidence inventory and reconstruction contract

- Goal: Establish the authoritative evidence inventory, coverage dimensions, uncertainty rules, and reconstruction acceptance contract.
- Capability slot: `workflow-orchestration`
- Owner skill: `software-development-orchestrator`
- Scope: Repository structure, current spec coverage, source/test/config evidence, and completeness gaps.
- Non-goals: Author target requirements or behavior specs before the inventory is stable.
- Dependencies: GitHub Issue #2 and a current code knowledge graph.
- Validation: Evidence paths exist; coverage matrix includes every bounded context, host, use case, adapter category, and cross-context contract.
- Commit checkpoint: Combine with the first validated durable specification batch.

### RECON-002 — Requirement baseline

- Goal: Author reconstructable system and bounded-context requirements with explicit assumptions and unknowns.
- Capability slot: `requirements`
- Owner skill: `requirement-author`
- Dependencies: RECON-001.
- Validation: Requirement guide conformance and evidence traceability.
- Commit checkpoint: Requirement baseline plus narrow validation.

### RECON-003 — Architecture reconstruction blueprint

- Goal: Specify architectural constraints, project topology, dependency rules, runtime composition, persistence, messaging, and observability at implementation-ready precision.
- Capability slot: `architecture`
- Owner skill: `ddd-ca-hex-architect`
- Dependencies: RECON-001 and RECON-002.
- Validation: Blueprint covers all 22 product projects, six hosts, three bounded contexts, shared contracts/building blocks, and deployment topology.
- Commit checkpoint: Architecture blueprint plus narrow validation.

### RECON-004 — Domain, use-case, API, message, persistence, and configuration specs

- Goal: Normalize and fill production specifications for every evidenced behavior and contract.
- Capability slot: `specification`
- Owner skill: `spec-author`
- Dependencies: RECON-002 and RECON-003.
- Validation: Bidirectional traceability between requirements, specs, source evidence, and reconstruction components.
- Commit checkpoint: Cohesive specification batch plus schema and link validation.

### RECON-005 — Validator-ready behavior and test oracle baseline

- Goal: Add structured problem frames and test-oracle coverage for reconstruction-critical use cases and cross-context journeys.
- Capability slot: `problem-framing`
- Owner skill: `problem-frame-author`
- Dependencies: RECON-004.
- Validation: Problem-frame syntax and selected spec-compliance gates; inferred facts remain marked.
- Commit checkpoint: Problem frames and test oracles plus focused validators.

### RECON-006 — Reconstruction-readiness audit

- Goal: Verify that the durable artifacts are self-contained, source-independent as instructions, and honest about residual gaps.
- Capability slot: `review`
- Owner skill: `software-development-orchestrator` using a reconstruction-specific checklist; no .NET code-review claim.
- Dependencies: RECON-001 through RECON-005.
- Validation: Fresh-context document walk, traceability checks, workflow validators, and repository validation selected by policy.
- Commit checkpoint: Final validated coherent batch and workflow closeout commit.

### RECON-007 — Inventory test ownership and compliance remediation

- Goal: Add an Inventory-owned test project, close the executable ReserveInventory gaps, and encode external-service tests as explicit opt-in checks.
- Capability slot: `implementation`
- Owner skill: `slice-implementer`, with test design governed by `bdd-gwt-test-designer`.
- Dependencies: RECON-005 failed-closed compliance report and the user's explicit test-policy authorization.
- Validation: Broker-free Inventory tests pass by default; external tests are skipped without opt-in; selected compliance remains fail-closed until every category is proven.
- Commit checkpoint: Inventory test surface and compliance remediation checkpoint.

### RECON-008 — Kafka ownership decisions and Inventory reservation source outbox

- Goal: Make Kafka canonical, define producer ownership, demonstrate one atomic Inventory source-outbox slice, correct Inventory event names, and strengthen the reconstruction gate.
- Capability slot: `implementation`
- Owner skill: `slice-implementer`, with architecture and specifications owned by their routed skills.
- Dependencies: RECON-007, the ReserveInventory problem frame, and the user's decisions on 2026-08-27.
- Validation: Broker-free tests pass by default; stable relay metadata is executable; PostgreSQL/Kafka and clean-room evidence remain fail-closed until run.
- Commit checkpoint: Kafka decision, Inventory source outbox, event corrections, specifications, tests, and validation evidence.

## Role Execution Coordination

| Stage | Role / Canonical Path | Owning Skill | Final/Current Disposition | Attempt Summary | Final Integration Owner / Decision | Record or Task Reference |
| --- | --- | --- | --- | --- | --- | --- |
| RECON-005 | `problem-frame-sub-agent` / `.ai/assets/sub-agent-role-prompts/problem-frame-sub-agent/sub-agent.yaml` | `problem-frame-author` | direct | One parent-inline attempt completed; no child invocation | `problem-frame-author` / accepted | `tasks/RECON-005.json`; `evidence/problem-frame-role-execution.yaml` |
| RECON-007 | `usecase-test-sub-agent` / `.ai/assets/sub-agent-role-prompts/usecase-test-sub-agent/sub-agent.yaml` | `slice-implementer` | direct | Parent-inline execution selected because the test project move and assertions share one mutation scope | `slice-implementer` / accepted | `tasks/RECON-007.json`; `evidence/inventory-test-role-execution.yaml` |
| RECON-008 | `outbox-sub-agent` / `.ai/assets/sub-agent-role-prompts/outbox-sub-agent/sub-agent.yaml` | `slice-implementer` | direct | One overlapping transaction, SQL, relay, and DI scope; delegated agents were not requested | `slice-implementer` / provisionally accepted | `tasks/RECON-008.json`; `evidence/inventory-outbox-role-execution.yaml` |
| RECON-008 | `usecase-test-sub-agent` / `.ai/assets/sub-agent-role-prompts/usecase-test-sub-agent/sub-agent.yaml` | `slice-implementer` | direct | Transaction, contract, and relay tests overlap the same implementation slice | `slice-implementer` / accepted | `tasks/RECON-008.json`; `evidence/inventory-outbox-test-role-execution.yaml` |

## Approval Gates

| Transition | Status | Authorization Source | Pending Decision |
| --- | --- | --- | --- |
| reverse engineering -> requirement/specification authoring | `approved` | User request and GitHub Issue #2 | None |
| requirement/design/specification -> product implementation | `not-required` | Product source changes are outside scope | None |
| failed compliance -> test implementation | `approved` | User request on 2026-08-26 and GitHub Issue #2 | None |
| architecture/specification -> Inventory source-outbox implementation | `approved` | User decisions on 2026-08-27 and GitHub Issue #2 | Final transaction-port shape remains an owner review gate |

## Validation Strategy

- Requirement/spec traceability: Every normative statement links to requirement/spec IDs and repository evidence; unknowns and aspirations use explicit status markers.
- Architecture validation: Reconcile the blueprint with solution/project/config facts and the current code graph.
- Test and implementation validation: Build and test the changed Inventory slice, then run the full default solution profile; keep external-service tests explicitly opt-in.
- Review/compliance gates: Validate workflow artifacts, document links/structure, problem-frame schemas, and the selected unchanged 100% gate; require two independent source-free LUNA-class reconstructions before any deletion decision.

## Test Execution Contract

- Provider: `target-profile-commands`
- Target-owned working directory: repository root
- Target-owned commands: To be resolved from current repository evidence during RECON-001.
- Prerequisites and environment boundary: .NET SDK from `global.json`; container-dependent checks remain conditional.
- Target policy: `.dev/project-config.yaml#validation.routine.local.mode=manual`
- Default selected levels: `unit`, `integration`
- Conditional selected levels and activation source: Environment-dependent runtime/E2E only if required by an existing target contract.

| Level | Outcome | Evidence | Deferral Owner / Follow-up |
| --- | --- | --- | --- |
| unit | passed | Full default solution profile: 63 passed. | None. |
| integration | passed default / blocked external | Inventory: 27 passed and one PostgreSQL test skipped; relay behavior is broker-free. | Start PostgreSQL and Kafka and opt in before counting real-store/order evidence as passed. |

## Spec Compliance Selection

- Selected: `yes`
- Activation source: Problem-frame workflow and repository mandatory 100% gate.
- Outcome: failed closed at 89% for the expanded ReserveInventory CBF checklist; real PostgreSQL rollback/concurrency evidence remains incomplete.
- Coverage and evidence: `reports/05-spec-compliance-report.md`; 100% remains mandatory.

## Progress And Handoff

- Current stage: RECON-008.
- Completed stages: RECON-001 through RECON-004; RECON-005 authored its artifacts and remains blocked on the remediation and unchanged 100% gate.
- Deferred stages and reasons: RECON-006 cannot close while selected compliance is below 100% and both source-free reconstruction exercises are unrun.
- Resolved decisions: Kafka canonical; producer owns event meaning/schema; ReserveInventory source outbox provisional; event names corrected; two LUNA-class reconstruction runs required provisionally.
- Open decisions: final transaction-port shape, outbox retention, other Inventory outbox adoption, RabbitMQ broadcast/dual deployment, and downstream consumer business ownership.
- Continuation instructions: Read `workflow.yaml`, this plan, `tasks/RECON-008.json`, reports 05-07, ADR-003, and ADR-004; inspect the concrete design, obtain external evidence, and run the unchanged 100% gate.
- Target policy references: `.dev/standards/WORKFLOW-GATE-POLICY.md`, `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md`, `.dev/TEAM-GIT-FLOW-RULES.MD`, `.dev/project-config.yaml`.
- Registered handoff checkpoint: None; this session remains active.
- Branch history and checkpoint handoffs: Segment 1 started from `main` at `59d651e`.

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `codex/2026-08-26-reconstructable-system-specification` | `main` | active | `a4b0f09f06bdfca9d8ea4e3e7e57ad68102fb15e` | local only | `2026-08-26T20:25:13+08:00` | Inventory test/compliance checkpoint; workflow remains open | Run opted-in PostgreSQL evidence, then resume RECON-005/RECON-006 |
| 1 | `codex/2026-08-26-reconstructable-system-specification` | `main` | active | `e093efe78723323134111f01632a7b45cc07aa28` | local only | `2026-08-27T08:53:12+08:00` | RECON-008 implementation baseline before local checkpoint | Commit the validated source-outbox slice; no remote mutation |

## Completion Summary

- Outcome: Documentation baseline and provisional Inventory source-outbox slice established; workflow remains in progress because external and reconstruction proof is incomplete.
- Changed artifacts: Reconstructable requirements, ADRs, architecture blueprint, message/persistence/runtime specs, ReserveInventory CBF, Inventory transaction/outbox/relay code and SQL, event contracts, tests, and workflow evidence.
- Approved requirement/specification evidence: User request and Issue #2 authorize drafting; content approval remains distinct from authorship.
- Implementation completion evidence: The provisional Inventory transaction/outbox/relay architecture compiles; broker-free transaction, retry, metadata, and contract tests pass.
- Required test outcomes: 63 default tests passed solution-wide; one Inventory PostgreSQL check is skipped and remains blocked-by-environment.
- Selected compliance evidence: ReserveInventory CBF is 89% and NOT COMPLIANT under the expanded 82-item checklist; `reports/05-spec-compliance-report.md`.
- Review disposition: Conditional; do not delete source yet. See `reports/06-reconstruction-readiness-audit.md`.
- Validation evidence: JSON/YAML parse, Markdown links, workflow validator, targeted builds, and broker-free tests passed; the external PostgreSQL gate is blocked-by-environment. See `reports/07-validation-summary.md`.
- Workflow task state: RECON-001 through RECON-004 completed; RECON-005 and RECON-007 blocked on external evidence; RECON-008 in progress pending owner design review, external evidence, and clean-room runs; RECON-006 pending.
- Commits: `3a5fbb3bb9bd5e4643af87ddfcbd6883373eb1fb`, `a4b0f09f06bdfca9d8ea4e3e7e57ad68102fb15e`.
- Branch / checkpoint / handoff evidence: Local branch created; no push, PR, merge, or handoff.
- Residual risks: Existing implementation may contain accidental behavior; the provisional port may be revised; PostgreSQL/Kafka and two clean-room LUNA acceptance exercises remain non-passing.

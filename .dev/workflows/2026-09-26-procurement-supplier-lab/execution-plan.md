# Execution plan and attribution

Workflow: 2026-09-26-procurement-supplier-lab. Issue: #17. Primary record: `.dev/workflows-v2/wf-28ef2d2ffe044802a4ddba263d5e5471.workflow.json`. All task worktrees belong to this single workflow; no task creates a successor workflow. Root is the final integration/review owner. Owner final review stays pending after delivery.

| task_id | owner_skill | model / reasoning_effort | Owned result |
| --- | --- | --- | --- |
| T001 | requirement-author, ddd-ca-hex-architect, spec-author | parent configured gpt-6-astra / ultra | Requirements, architecture, entity/production/adapter and formal-test specifications |
| T002 | slice-implementer (generic) | gpt-6-luna / high | Supplier sandbox, WireMock host/control UI, Microcks artifacts, focused tests |
| T003 | slice-implementer (generic) | gpt-6-sol / high | Procurement domain, application, persistence, provider HTTP adapter, API/outbox and focused tests |
| T004 | slice-implementer (generic) | gpt-6-sol / high | Inventory receipt transaction, event consumer, additive SQL and tests |
| T005 | slice-implementer (generic) | assigned on dispatch | Compose integration, lab scripts and runbook |
| T006 | code-reviewer, spec-compliance-validator | parent configured gpt-6-astra / ultra | Review, actual acceptance evidence and model observations |

Actual child invocation establishes child model attribution. Parent model is from configured default because the exact parent runtime model string is not separately exposed. Task status and timestamps are owned by the primary tool-created record and its history; these are planned assignments, not claims of execution.

Routine workers receive one bounded envelope with authorization, owned paths, baseline specifications, applicable rule packets, stop conditions and parent integration owner. Each worktree has one tracked writer; read-only reviewers may coexist. Workers must not edit workflow records, shared source-of-truth outside their scope, push, merge, create Issues or invoke other workflows. They report actual commands, failures, repairs, residual uncertainty and final local commit. Root integrates reviewed local commits.

Evaluation keeps first delivery separate from corrections. Task difficulty and scope differ, so outcomes are engineering observations rather than a controlled model ranking. Record exact input commit/specs, model/effort, changed paths, build/test outcomes, review findings and retry outcomes. Wall-clock, token and cost metrics are unavailable unless genuinely provided by the runtime; do not estimate them as measured values.

## Preflight observations

- Baseline local/remote main: cc0e345367a1d24f49bf8fa68e0eb668df9e5e55. Framework receipt freshly admitted against identical full tree 1f1bac4fcc564657ae8eddb4ee1c704cc85c7284 in existing rc1 pilot worktree. No authority bytes changed.
- Target effective packets resolved for selected authoring, architecture, implementation, review and compliance selectors; raw results are in ignored `artifacts/procurement-lab/effective-rules`.
- Docker engine responded at 29.8.0. Existing unrelated observability Compose project remains running; commerce project was not listed as running. No data/volume deletion authorized.
- Hosted Issue creation initially rejected by automatic approval; owner explicitly authorized it, then Issue #17 was created. Initial sandbox network/Docker/other-worktree read failures remain actual preflight failures, resolved through approved scoped access.
- Code graph has stale Inventory implementation edges/snippets. Graph remains discovery only; implementation uses current tracked source on the baseline.

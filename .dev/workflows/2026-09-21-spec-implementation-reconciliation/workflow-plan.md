# Specification and implementation reconciliation

## Workflow Metadata

- `workflow_id`: `2026-09-21-spec-implementation-reconciliation`
- `plan_id`: `development-plan-2026-09-21-spec-implementation-reconciliation`
- `owner_skill`: `software-development-orchestrator`
- `branch`: `codex/2026-09-21-spec-implementation-reconciliation`
- `base_branch`: `main`
- `status`: `in_progress`
- `created_at`: `2026-09-21T11:15:46+08:00`
- `updated_at`: `2026-09-21T11:29:37+08:00`
- `template_source`: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `template_version`: `1.4.0`
- Work item: [#2](https://github.com/YuChia-Wei/dotnet-distributed-architecture-lab/issues/2).

## Authorized outcome and boundaries

The 2026-09-21 owner request authorizes repairing the preceding specification/code review findings. Prefer the newer semantic implementation, contract, or explicit decision; incidental edits, generated snapshots, and copied observations do not establish a changed business decision. Consolidate genuinely unresolved choices for one owner decision batch. Starting subject: `2ee6ee21cfe64da4b87b8c57b5a661b9b9a8f517`.

Preserve Inventory EF Core, Products/Orders Dapper, producer ownership, existing wire names, Kafka canonical transport, existing source outbox transaction boundaries, and current stored data. Keep intentional reconstruction quality uplifts and unfinished clean-room work explicit. Do not rewrite dated historical validation records or infer current execution from them. Provider Issue closeout and release are outside this repair.

## Delivery and execution choice

One workflow groups documentation reconciliation and the related executable messaging corrections. Its unique state is the semantic-history disposition ledger, bounded owner decision, separate writer/reviewer handoff, and exact validation checkpoint; these make it independently resumable. One tracked writer per worktree. Read-only history workers may run concurrently. Use a dedicated branch and the repository's `--no-ff` strategy if integration is selected. Do not treat an unresolved acceptance as completed.

## Tasks and skill ownership

- SYNC-001: `spec-author`, with `requirement-author` and `problem-frame-author` for the existing artifact types: reconcile current requirements, production/test specs, the selected CBF event shape, manifests and operations documentation.
- SYNC-002: `slice-implementer`, generic remediation: repair the Orders source-outbox occurrence-time contract after temporal disposition, with focused serializer/relay tests.
- Inventory replay after finite retention: hold only dependent behavior changes until the single owner decision is resolved; add the bounded implementation task if selected.
- `code-reviewer`: independently inspect the final diff and acceptance evidence. Routine same-runtime discovery/implementation uses bounded invocation/results; full evidence applies to terminal or external validation only.

## Acceptance criteria

- AC1: Every review finding has a source-bound temporal disposition or explicit unresolved owner question in `decisions.md`.
- AC2: Current technology, project/dependency inventory, event shapes, queries, relay completion and test-status documentation agree with the selected authority.
- AC3: Orders outbox reconstruction preserves original event occurrence time across serialization and retry, if confirmed as the newer contract; all four event types retain existing producer call sites and wire fields.
- AC4: Inventory replay after cleanup has a selected contract and a meaningful combined persistence test, or remains explicitly pending owner decision without a completion claim.
- AC5: Prior PostgreSQL/Kafka results remain dated and subject-bound; unexecuted Products/Orders database tests, intended quality uplifts and clean-room reconstructions remain non-passing where applicable.
- AC6: Focused tests, structured-document checks, target governance, and independent diff review report actual outcomes; worktree and commit evidence remain truthful.

## Validation selection

Target routine policy is local `manual`, CI `unconfigured`; no implicit routine validator activation. The repair explicitly selects focused Orders tests, a real PostgreSQL Inventory test only if behavior is selected, structured JSON/YAML/manifest and requirement-reference checks, and lifecycle target governance. Preserve Compose volumes and initial stopped state if database execution is needed. No Kafka/E2E rerun is selected for documentation and serializer-only edits. No whole-system spec-compliance or clean-room acceptance is selected: the CBF edit is bounded source-shape reconciliation, not a claim of full problem-frame implementation compliance.

Long/full-matrix validation requires a clean immutable subject and the repository's external-task contract. Narrow tests may run inline. Historical passing checks are not silently relabeled as current-head execution.

## Progress and next action

Semantic history dispositions and the consolidated two owner decisions are recorded in [decisions.md](decisions.md). SYNC-002 is implemented and its focused red/green execution is recorded in the task. SYNC-001 remains active for settled document reconciliation and the unresolved R02/R07 choices. Continue from this branch; do not change dependent Inventory replay behavior or the persisted domain-event schema before the owner selects them. The [bounded verification record](evidence/checkpoint-verification.json) records 10 passing focused tests, document parity checks and an independent six-file review with no reportable findings. This is a partial checkpoint; final acceptance still requires the two owner decisions and their selected repairs/validation. Workflow completion and integration remain pending acceptance.

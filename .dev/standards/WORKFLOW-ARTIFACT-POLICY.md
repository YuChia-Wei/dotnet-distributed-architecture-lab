# Workflow Artifact Policy

This policy defines the repository-wide discovery and metadata contract for durable workflows. It does not define one universal plan, task, or report shape.

## Ownership Boundary

- Every skill that can create a workflow owns the templates and domain-specific layout it creates.
- A skill may define its workflow topic, task IDs, report set, and artifact root.
- The repository owns only the minimum discovery, identity, time, relationship, and lifecycle contract in this document.
- `software-development-orchestrator` owns software-development workflow templates. It does not own templates for AI context maintenance, repository initialization, or every other workflow kind.

## Workflow Discovery Locator

Every workflow created on or after 2026-07-10 must have this locator, even when its artifacts are stored elsewhere:

```text
.dev/workflows/<workflow-id>/workflow.yaml
```

Required locator fields:

```yaml
schema_version: "1.0"
lifecycle_contract: "1.0"
workflow_id: "YYYY-MM-DD-topic"
workflow_kind: "skill-defined-kind"
title: "Human-readable title"
owner_skill: "workflow-owning-skill"
status: "in_progress"
artifact_root: ".dev/workflows/YYYY-MM-DD-topic"
entrypoint: "workflow-plan.md"
created_at: "2026-07-10T18:17:55+08:00"
updated_at: "2026-07-10T18:17:55+08:00"
template_source: ".ai/assets/skills/<owner-skill>/templates/workflow-locator-template.yaml"
template_version: "1.0.0"
branch: "<runtime-prefix>/YYYY-MM-DD-topic"
base_branch: "main"
```

The locator may contain additional skill-specific fields. Required field names and meanings must not be changed by a skill template.

For workflows created on or after 2026-07-11, `branch` and `base_branch` are also required. The workflow branch must differ from the base branch and must not be `main` or another long-lived trunk.

## Branch Metadata And Continuation

- Create the dedicated workflow branch before the locator or material workflow edits.
- Default Codex naming to `codex/<workflow-id>`; use the active runtime or repository prefix when another convention applies.
- Keep `base_branch` as the integration branch from which the current workflow segment started.
- Treat `branch` as the current or most recent dedicated workflow branch. Update it when an incomplete workflow continues on a new branch after a checkpoint merge.
- Record push and merge handoff evidence in the plan or a skill-owned history field, including the resume source and action.
- A push-only handoff normally keeps the same branch; a checkpoint merge starts the next branch segment from the updated target branch.
- A checkpoint push or merge does not change `status` to `completed`; pending tasks and exact continuation instructions remain durable.
- Conversely, `status: in_progress` does not block an otherwise authorized push, pull request, or merge. Transport and workflow completion are independent facts.
- A historical active workflow without branch metadata must add branch metadata when it next resumes, after creating its continuation branch.

## Workflow ID

- Use `YYYY-MM-DD-<skill-owned-topic>[-<sequence>]`.
- The date is the local calendar date when the workflow is created.
- Keep the ID immutable after creation.
- Resolve a same-day collision with `-02`, `-03`, or a concise semantic suffix.
- A skill may define the topic and suffix but must preserve the sortable full-date prefix.
- Do not rename historical month-only workflows merely to conform. Preserve their paths and treat them as legacy artifacts.

## Artifact Root

- Default to `.dev/workflows/<workflow-id>/`.
- A skill may select another repository-relative, Git-trackable artifact root when its workflow design requires it.
- Keep the discovery locator at `.dev/workflows/<workflow-id>/workflow.yaml` when a non-default root is used.
- The locator `entrypoint` must resolve inside the declared artifact root and must lead to current progress, next work, blockers, and deferred items without repeating repository analysis.
- Do not use ignored, generated, dependency, temporary, or repository-external locations.
- Do not store runtime workflow records inside `.ai/assets/skills/`, `.agents/skills/`, or `.claude/skills/`.
- Do not let two active workflows share one artifact root.
- Treat `artifact_root` as immutable. If relocation is necessary, update the locator and every active reference and record the origin in the destination artifacts.

## Time Metadata

- Use ISO 8601 / RFC 3339 timestamps with seconds and an explicit UTC offset.
- `created_at` is the actual artifact creation time and is immutable. It is not a Git commit timestamp.
- `updated_at` changes when content, status, ownership, artifact relationships, progress, or conclusions change materially.
- Formatting-only changes do not require a timestamp update.
- Derived artifacts such as translations have their own timestamps and a `derived_from` relationship. Creating a derived artifact does not update the canonical source timestamp.
- If a legacy timestamp is reconstructed, record `created_at_source: git-history | file-evidence | inferred`; do not present an inferred time as directly observed.

## Skill-Owned Templates

Every workflow-producing skill must declare its templates and defaults in its canonical skill spec. A template must include template metadata equivalent to:

- `template_id`;
- `template_version`;
- `template_created_at` and `template_updated_at`, or a clearly scoped Template Metadata section containing `created_at` and `updated_at`.

Artifacts generated from a template must record `template_source` and `template_version` when the format supports metadata.

The skill may define additional workflow, task, report, and status fields. Shared compatibility requires only the locator and the minimum task relationship fields below.

## Task Minimum Contract

Every durable task must include:

- `task_id`;
- `workflow_id`;
- `owner_skill`;
- `status`;
- `created_at`;
- `updated_at`;
- `template_source`;
- `template_version`.

For tasks created on or after `2026-07-27T09:52:09+08:00`, also require:

- `model` for the primary executing AI model;
- `reasoning_effort` for the primary executor's reasoning setting.

An unfinished task created earlier must add these two fields the next time it
is materially updated on or after the effective timestamp. Do not backfill a
completed historical task. Resolve values from the active session when
available; otherwise use the effective configured default after the client's
documented precedence, then its documented built-in default. Preserve the
reported or configured strings without cross-provider normalization. Additional
sub-agent contributors belong in marked Git trailers under
`GIT-COMMIT-POLICY.md`, not in extra task fields.

Task IDs are immutable, path-safe, and unique within the workflow. Use `<workflow-id>#<task-id>` for cross-workflow references. A skill may define its own task ID prefix and task body.

Use these shared lifecycle states when they apply:

```text
pending -> in_progress -> completed
```

Use `deferred` only with a recorded reason and handoff condition. Skills may add domain-specific states without redefining the shared meanings.

Locators generated from template version `1.2.0` or later opt into
`lifecycle_contract: "1.0"`. Under that prospective contract:

- an `in_progress` workflow has exactly one `in_progress` task;
- a `completed` workflow has no unfinished task and uses `completed` or `closed` as `current_phase`;
- a completed task has a non-empty result summary and an addressed finding status;
- legacy locators without the field remain compatible and are not silently reinterpreted.

## Declared Terminal Anchor Reconciliation

A workflow may opt into terminal-anchor schema `1.0` by adding the mapping
below to its locator. This contract is relationship-driven. A
validator must not infer an anchor or its effect from a workflow title,
directory, date, version string, task prose, or hard-coded release list.

```yaml
terminal_anchor_contract:
  schema_version: "1.0"
  anchors:
    - anchor_id: "<path-safe-stable-id>"
      anchor_kind: "<declared-lifecycle-kind>"
      evidence_ref: ".dev/workflows/<workflow-id>/evidence/<evidence>.yaml"
      on_satisfied: "complete | continue"
      continuation:                 # required only for continue
        reason: "<why work remains after this anchor>"
        task_ids:
          - "<unfinished-task-id>"
```

`evidence_ref` is an exact repository-relative Git-trackable file. It has this
machine-readable shape:

```yaml
schema_version: "1.0"
evidence_id: "<path-safe-stable-id>"
anchor_id: "<matching-anchor-id>"
observed_state: "satisfied | not-satisfied | unknown"
observed_at: "<ISO-8601-with-offset>"
source:
  kind: "<evidence-source-kind>"
  references:
    - "<source-reference>"
facts:
  <fact-name>: <observed-value>
```

- Capture live provider or external-system observations before committing
  evidence that depends on them. The tracked observation is the deterministic
  offline validation input; ordinary validation must not require ambient
  credentials or refresh the provider.
- `on_satisfied: complete` requires `status: completed` and terminal tasks when
  the evidence state is `satisfied`.
- `on_satisfied: continue` is an explicit non-terminal relationship. It
  requires a reason and the exact unfinished task IDs; every declared task must
  exist and, while the workflow is active, the declaration must equal the full
  unfinished-task set.
- `not-satisfied` and `unknown` evidence do not create a terminal claim. A
  malformed, missing, mismatched, duplicated, or unsafe declaration fails
  closed.
- Adding this contract is prospective and explicit. Historical workflows
  without it remain compatible and are not classified from naming patterns.

`validate-workflow-artifacts.py` reports the workflow ID, anchor ID, task ID,
and conflicting state for actionable stale-projection failures.

## Workflow Completion

`status: completed` means workflow completion only: every workflow-owned task
is terminal and the selected lifecycle contract is satisfied. The contextual
alias `workflow closeout` may be used inside this section, but it does not mean
repository integration, assessment finality, release-source validation,
hosted publication, or publication finalization. Evidence for any of those
separate events remains with its own owner.

A provider-only review, hosted check, admission, integration, or post-merge
read-back that creates no remaining workflow-owned implementation task does not
keep the workflow `in_progress`. Track that operation under its provider or
terminal policy. Do not create a tracked evidence-sync commit merely to copy a
later provider state into an already completed implementation workflow.

## Final and Derived Artifacts

- Do not silently overwrite a final baseline, review, or verification report.
- Correct a final artifact through an explicit reopen, corrigendum, addendum, or successor report.
- Record canonical-versus-derived relationships for translations and generated views.
- Preserve finding and decision IDs across remediation and verification artifacts.
- For a workflow binding multiple work items, preserve separate acceptance IDs,
  outcomes, and evidence digests in a machine-readable ledger and its matching
  human report projection; one aggregate success flag is insufficient.
- Record validation freeze, reuse receipt, agent execution packet, worktree
  lease, graph freshness or tracked fallback, retry decision, and terminal
  release as separate artifacts when those lifecycle states apply.

## Validation and Legacy Boundary

- New workflows dated 2026-07-10 or later must satisfy this policy.
- Historical workflows may retain month-only IDs and older layouts.
- When a historical workflow remains active, add a new locator or migration note instead of silently rewriting its identity.
- Validate new locators, timestamps, artifact roots, entrypoints, task identity, and task timestamps with `.ai/scripts/validate-workflow-artifacts.py`.
- Validate `branch` and `base_branch` for workflows dated 2026-07-11 or later.

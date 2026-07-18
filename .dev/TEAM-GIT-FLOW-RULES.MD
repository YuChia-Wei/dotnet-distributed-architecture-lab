# Repository Branch And Merge Policy

This document is the canonical owner of repository branch naming, workflow
branch lifecycle, checkpoint handoff, push continuation, and merge strategy.

The repository uses a single-trunk, short-lived-branch model. It is
GitHub-Flow-like because work branches start from and return to `main`, but it
adds repository-specific workflow artifacts, checkpoint continuation, and a
default `--no-ff` merge rule. It is not classic Git Flow: there is no persistent
`develop`, release, or hotfix integration hierarchy. It is also not strict
trunk-based development because workflow-mode changes do not occur directly on
`main`.

## Core Rule

`main` is the only long-lived trunk.

All feature, workflow, documentation, and agent work branches start from `main`. Completed workflows merge back to `main`; an explicitly requested earlier merge is a checkpoint and does not close the workflow.

## Branch Model

### Long-Lived Branches

| Branch | Role |
| --- | --- |
| `main` | Single trunk and integration branch. Must stay coherent and reviewable. |

Do not create persistent `develop`, `baseline`, `release`, or agent-specific long-lived branches for normal work.

### Short-Lived Branches

Use short-lived branches for bounded work. When workflow mode applies, a
dedicated workflow branch is mandatory. Direct mode remains governed by
`.dev/standards/WORKFLOW-GATE-POLICY.md` and does not create workflow artifacts.

| Prefix | Use |
| --- | --- |
| `codex/` | Codex-owned workflow or task branch. |
| `claude/` | Claude-owned workflow or task branch. |
| `docs/` | Human-authored documentation branch when no agent prefix is appropriate. |
| `fix/` | Small human-authored fix branch when no agent prefix is appropriate. |

Use the agent prefix when an agent performs the work.

## Normal Flow

1. Start from a clean `main`.
2. Create or switch to a short-lived branch before workflow artifacts or material edits:

   ```text
   <prefix>/<topic>
   ```

3. Make focused commits following `.dev/standards/GIT-COMMIT-POLICY.md`.
4. Run the narrowest meaningful validation.
5. Merge back to `main` with no fast-forward:

   ```bash
   git checkout main
   git merge --no-ff <branch-name>
   ```

6. Confirm `main` is clean after merge.

## Workflow Branches

When work uses `.dev/workflows/<workflow-id>/`, use:

```text
codex/<workflow-id>
claude/<workflow-id>
```

Examples:

```text
codex/2026-07-11-ai-context-skill-and-doc-cleanup
claude/2026-07-11-payment-refactor-stage-1
```

Create the branch before creating `.dev/workflows/<workflow-id>/workflow.yaml`. Record the branch and base branch in the locator.

## Assessment Branches

Standalone durable assessments use a dedicated short-lived branch without a
workflow locator:

```text
codex/assessment/<lowercase-assessment-id>
claude/assessment/<lowercase-assessment-id>
```

Create the branch before `.dev/assessments/<assessment-id>/assessment.yaml` or
the report. Keep assessed surfaces read-only and commit only assessment-owned
artifacts plus required assessment index updates. If an assessment is produced
inside an existing authorized workflow, use the workflow branch instead of
creating a competing assessment branch.

Assessment branches follow the normal `--no-ff` merge rule unless the user
explicitly selects another strategy.

## Merge Rule

Use `--no-ff` for workflow and multi-commit branches so the branch work remains visible as a grouped unit.

Fast-forward merge is acceptable only for tiny direct-mode branches when the user or maintainer explicitly chooses it.

## Checkpoint Handoff And Cross-Machine Continuation

When work must move to another machine or session before all workflow tasks are complete:

1. Commit a coherent validated checkpoint and keep the workflow `active`.
2. Prefer pushing the workflow branch when integration into `main` is not required.
3. For a push-only handoff, fetch the remote branch on the next machine and resume that branch, or create a continuation branch from that remote branch. Do not restart from `main`, because it does not contain the unmerged checkpoint.
4. If merge is explicitly requested, merge with `--no-ff` and push the requested target.
5. After a checkpoint merge, start from the updated target branch and create a new continuation branch such as `<prefix>/<workflow-id>-cont-02`; do not continue material work on the target branch.
6. Record the checkpoint type (`push` or `merge`), commit, remote or target, timestamp, reason, last completed task, and exact resume branch/action in the workflow plan.
7. Update locator `branch`, `base_branch`, `updated_at`, and branch history only when the active branch segment changes.

A checkpoint push or merge is a transport and handoff boundary. Neither is a workflow completion signal.

## Commit Rule

Commit formatting and commit timing are defined in:

```text
.dev/standards/GIT-COMMIT-POLICY.md
```

Do not duplicate detailed commit message rules here.

## Workflow Gate

When deciding whether a task needs a workflow branch and workflow artifacts, follow:

```text
.dev/standards/WORKFLOW-GATE-POLICY.md
```

## Cleanup Before Merge

Before merging a short-lived branch back to `main`:

- confirm workflow task statuses are accurate;
- confirm validation was run or skipped with a documented reason;
- remove accidental temporary files;
- keep intentional workflow artifacts when they are part of the decision trail;
- run `git status --short` and confirm only intended changes were committed.

## Outdated Branch Models

The following branch models are not used for current work:

- `develop` as a second long-lived integration line;
- agent-specific long-lived branches.

Reintroduce any of these only after updating this document and the related workflow policy.

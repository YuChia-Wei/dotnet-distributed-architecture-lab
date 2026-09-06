# Workflow and Commit Playbook

Use this playbook when AI context cleanup is large enough to need workflow tracking or commits.

## Workflow Gate

Check `.dev/standards/WORKFLOW-GATE-POLICY.md`.

Create a workflow when cleanup:

- changes source-of-truth rules;
- reorganizes `.ai`, `.dev`, `.agents`, or `.claude`;
- affects future agent behavior;
- crosses skill boundaries;
- needs multiple stages or task status.

## Skill-Owned Workflow Contract

Use the workflow templates owned by this skill for AI context maintenance. Do not depend on a universal workflow body template.
Branch naming, push handoff, checkpoint merge, continuation, and merge strategy follow `.dev/TEAM-GIT-FLOW-RULES.MD`; this playbook only describes their AI-context application.

- Create or switch to the dedicated workflow branch before creating the locator, plan, tasks, or remediation artifacts.
- Workflow id: `YYYY-MM-DD-topic[-NN]`.
- Default Codex branch: `codex/<workflow-id>`; record it with `base_branch` in the locator and plan.
- Stable locator: `.dev/workflows/<workflow-id>/workflow.yaml`.
- `artifact_root` may be the locator directory or another repository path selected for the task.
- Timestamps: ISO 8601 with an explicit offset, for example `2026-07-10T18:22:49+08:00`.
- Preserve `created_at`; update `updated_at` whenever an artifact changes.
- Generated artifacts must record `template_source` and `template_version`.

If the base id already exists, append `-02`, `-03`, and so on. Do not infer sequence from an ambiguous month-only directory name.

## Checkpoint Handoff

When the user requests merge or push before the AI-context workflow is complete,
`in_progress` is not by itself a blocker. Proceed only after the transport is
separately authorized, the required checkpoint is valid, and repository gates
pass:

- follow `.dev/standards/WORKFLOW-HANDOFF-POLICY.md`;
- commit a coherent validated checkpoint;
- select linear or merge-commit topology under `.dev/TEAM-GIT-FLOW-RULES.MD`;
- normally retain a merge commit when a checkpoint branch boundary carries
  durable resume or handoff evidence;
- keep the workflow and unfinished remediation tasks active;
- record the checkpoint type, commit, remote/target, last completed work, and exact next action;
- resume a push-only handoff from the pushed branch;
- after a checkpoint merge, resume from the updated target on a new dedicated continuation branch instead of editing the target branch.
- before a model, runtime, host, machine, or fresh-session transfer, create the
  machine-readable receiving checkpoint and verify it with
  `validate-workflow-handoff.py`;
- preserve provider-native Git attribution and keep unavailable provider
  fixtures explicitly blocked rather than inventing an identity.

## Commit Policy

Check `.dev/standards/GIT-COMMIT-POLICY.md`.

For workflow-stage commits, use exactly one of these alternatives:

```text
<type>(<scope>): <summary>
```

or:

```text
<type>(#<issue-number>): <summary>
```

The `|` character in historical examples was meta-notation for “or”, not a
literal part of a commit title. Follow the prospective and legacy-compatibility
boundary in `.dev/standards/GIT-COMMIT-POLICY.md`.

Include body sections:

- `Why`
- `What`
- `Validation`
- `Workflow`

## Task Updates

When completing a task:

- set `status` to `completed`;
- summarize changed files in `results.files_changed`;
- list validation in `results.tests_run`;
- leave `follow_up_needed` true only when another explicit task remains outside the current workflow.
- update the task's `updated_at` while preserving `created_at`.

## Terminal Anchor Reconciliation

Follow `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md` when an external lifecycle
event can make an active workflow projection stale.

- Declare the stable anchor relationship and exact Git-trackable evidence file;
  never derive the relationship from a title, directory, date, version, or
  hard-coded release list.
- Use `on_satisfied: complete` only when satisfying the anchor makes every
  workflow-owned task terminal.
- Use `on_satisfied: continue` only with the reason and exact unfinished task
  IDs for separately authorized work that truthfully continues after the
  anchor.
- Capture live provider evidence when creating or refreshing the observation,
  but keep ordinary validation deterministic and credential-free.
- Preserve earlier failed, blocked, and intermediate records with their
  original outcomes when reconciling the current workflow/task projection.

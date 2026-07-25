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

When the user requests merge or push before the AI-context workflow is complete:

- follow `.dev/standards/WORKFLOW-HANDOFF-POLICY.md`;
- commit a coherent validated checkpoint;
- use `git merge --no-ff` when merge is requested;
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

For workflow-stage commits, use:

```text
<type>(<scope>): <summary>
```

or with issue number:

```text
<type>(#<issue-number>|<scope>): <summary>
```

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

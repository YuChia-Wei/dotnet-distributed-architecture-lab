# Workflow Artifact Playbook

Use this skill's workflow artifacts when software or product development crosses lifecycle stages, needs development-skill or sub-agent handoff, or requires durable validation and commit checkpoints.

## Artifact Layout

```text
.dev/workflows/<workflow-id>/
  workflow.yaml
  workflow-plan.md
  review-report.md
  tasks/
    <task-id>.json
```

Use `YYYY-MM-DD-topic` for the workflow id. When the same topic is started more than once on the same date, append `-02`, `-03`, and so on. `workflow.yaml` is the shared locator; it declares the owner skill, artifact root, timestamps, and artifact paths. The development plan, tasks, and optional development review report are generated from this skill's templates.

Create or switch to `codex/<workflow-id>` or the active runtime equivalent before creating these artifacts. Record `branch` and `base_branch` in the locator and plan. Follow `.dev/TEAM-GIT-FLOW-RULES.MD` for branch naming, push handoff, checkpoint merge, continuation, and merge strategy. A merge/push before completion keeps the plan and pending tasks active: resume push-only handoffs from the pushed branch, and create a continuation branch from the updated target only after merge.

`review-report.md` is optional and should be created only when a development review output is produced. Its body comes from the development-specific template owned by this skill; the shared policy does not require this filename for other workflow kinds.

## Workflow Plan

The workflow plan should capture:

- metadata: plan id, owner skill, status, creation and update timestamps, and template source/version;
- problem statement and current scope;
- target direction and constraints;
- stages, goals, scope, risks, and recommended implementers;
- validation strategy;
- open questions and dependencies;
- completion summary when closed.

## Task JSON

Each task JSON should capture:

- `task_id`;
- `owner_skill`;
- `related_plan_id`;
- `status`;
- `created_at` and `updated_at`;
- `template_source` and `template_version`;
- scope target, files, dependency radius, constraints, and non-goals;
- inputs and user constraints;
- execution steps, validation, and deferred items;
- results after completion.

Use these statuses:

```text
pending -> in_progress -> completed
```

Use `deferred` only when the work is intentionally postponed and the task or plan explains why.

## Stage Update Rules

- Mark a task `in_progress` before making material edits for that task.
- Keep `created_at` immutable and update `updated_at` whenever material content or status changes. Use an ISO 8601 timestamp with an explicit UTC offset.
- Mark a task `completed` only after the task output exists and the narrow validation has passed.
- Record skipped validation when it would normally apply.
- Keep task results factual: changed files, commands run, and follow-up state.
- Do not close the workflow plan until final validation has passed.

## Skill-Owned Templates

- `../templates/workflow-locator-template.yaml`
- `../templates/development-workflow-plan-template.md`
- `../templates/development-workflow-task-template.json`
- `../templates/development-review-report-template.md`

These templates are owned by `dev-workflow` and describe development artifacts only. Do not reuse them for AI context audit, context governance, repository initialization, or documentation-only workflows.

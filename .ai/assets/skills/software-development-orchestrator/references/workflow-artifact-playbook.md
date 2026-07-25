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
- approval state and authorization sources for stage transitions;
- stages, goals, scope, risks, and recommended implementers;
- validation strategy, target-owned test execution, and selectable compliance;
- open questions and dependencies;
- completion summary with separately verified closeout evidence when closed.

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
- approval state, test execution records, and selected compliance state;
- results after completion.

When `execution.capability_slot` is `implementation`, replace the template's
null `implementation_contract` with:

```json
{
  "intent": "review-remediation",
  "execution_mode": "command",
  "overlays": ["remediation"],
  "authorization_source": ["<user request or workflow task reference>"],
  "normative_truth": ["<requirement, spec, standard, or ADR>"],
  "finding_evidence": ["<assessment-id>#<finding-id>"],
  "subject_revision": "<40-character Git SHA or empty string>",
  "acceptance_criteria": ["<observable completion criterion>"]
}
```

- Use exactly one `execution_mode`: `command`, `query`, `reactor`, or `generic`.
- Use the `remediation` overlay only with `review-remediation` or
  `validation-failure-remediation` intent.
- Keep authorization, normative truth, and finding evidence separate.
- Do not use deprecated `mode`, `source_truth`, or `source_findings` fields.
- Leave `implementation_contract` null for non-implementation tasks.

When `execution.capability_slot` is `test-execution`, replace the template's
null `test_execution_contract` with:

```json
{
  "provider": "target-profile-commands",
  "target_owned": {
    "working_directory": "<repository-relative path>",
    "commands": [
      {
        "level": "unit",
        "command": "<exact target-owned command>"
      },
      {
        "level": "integration",
        "command": "<exact target-owned command>"
      }
    ],
    "prerequisites": [],
    "environment_boundary": [],
    "policy": []
  },
  "selected_levels": ["unit", "integration"],
  "required_for_closeout": ["unit", "integration"],
  "conditional_selection_sources": [],
  "outcomes": [
    {
      "level": "unit",
      "outcome": "<passed | failed | blocked-by-environment | not-applicable | deferred-with-owner>",
      "evidence": [],
      "deferral_owner": "",
      "follow_up": ""
    }
  ]
}
```

- Provider order is `target-profile-commands`,
  `evaluated-external-skill`, then `fallback-contract`.
- Unit and integration are selected by default. Add E2E, browser, Playwright,
  or environment-dependent levels only with a recorded selection source.
- `required_for_closeout` is a subset of `selected_levels`. A required level
  must pass, or have a target-policy-backed `deferred-with-owner` outcome with
  an owner and follow-up, before the task can complete.
- A selected `not-applicable` level records why the target has no applicable
  command and is omitted from `required_for_closeout`; do not invent a command
  merely to satisfy the record shape.
- Record commands and environment requirements, not secrets. Never invent
  credentials, bypass controls, or escalate privileges implicitly.
- Leave `test_execution_contract` null for other capability slots.

Use these statuses:

```text
pending -> in_progress -> completed
```

Use `deferred` only when the work is intentionally postponed and the task or plan explains why.

## Stage Update Rules

- Mark a task `in_progress` before making material edits for that task.
- Keep implementation pending while requirement, design, or specification
  approval is unresolved. Record the authorization source before creating or
  executing implementation work.
- Keep `created_at` immutable and update `updated_at` whenever material content or status changes. Use an ISO 8601 timestamp with an explicit UTC offset.
- Mark a task `completed` only after the task output exists and the narrow validation has passed.
- Record skipped validation when it would normally apply.
- For test execution, record the provider, selected level, target-owned command,
  working directory, prerequisites, policy, and exactly one supported outcome.
  `blocked-by-environment` remains blocked and is never counted as passed.
- Record spec compliance as `not-applicable` when unselected. Once selected,
  require complete configuration and 100% coverage or fail closed.
- Keep task results factual: changed files, commands run, and follow-up state.
- Do not close the workflow plan until final validation has passed.

## Commit And Closeout Rules

- Use one validated commit per durable stage or coherent bounded batch, not one
  commit per skill invocation.
- Small tasks completed and validated together may share a commit.
- Fixup or squash only unshared, unpushed history under repository policy.
  Preserve approval baselines, review or evidence commits, pushed history, and
  checkpoint or handoff commits.
- Before closeout, verify approved requirements and specs, implementation
  completion, required test outcomes, selected compliance gates, review
  disposition, validation evidence, task state, commit evidence, and branch or
  handoff state separately.

## Fresh-Session Resume

For a fresh-session continuation, populate the locator `continuation` block
with the current task, target-policy references, and the registered handoff
checkpoint. The checkpoint owns the exact next action and must set
`hidden_context_required: false`. Resume from Git, the locator, current task,
target policy, recorded test state, and the validated checkpoint; hidden chat
state is never an input.

Run the repository handoff validator before continuation. A missing,
unregistered, stale, or mismatched checkpoint blocks the handoff.

## Skill-Owned Templates

- `../templates/workflow-locator-template.yaml`
- `../templates/development-workflow-plan-template.md`
- `../templates/development-workflow-task-template.json`
- `../templates/development-review-report-template.md`

These templates are owned by `software-development-orchestrator` and describe development artifacts only. Do not reuse them for AI context audit, context governance, repository initialization, or documentation-only workflows.

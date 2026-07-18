# Workflow Gate Policy

This policy defines when an agent should create workflow artifacts proactively instead of using direct mode.

## Default Modes

| Mode | Use |
| --- | --- |
| Direct mode | Small, single-pass work that does not need long-lived context. |
| Assessment mode | Read-only analysis that needs a durable report but does not authorize remediation or execution tracking. |
| Workflow mode | Multi-stage work that changes source-of-truth, crosses skill boundaries, or needs task status tracking. |

Mode is determined by intent, mutation, and execution tracking, not by the number of analysis steps alone. A transient read-only analysis may use multiple passes or sub-agents in direct mode when it does not write a repository report, mutate repository files, or perform remediation. A user request for a "report" means a durable repository artifact only when the user asks to save, persist, land, or otherwise retain it in the repository. Persistence by itself selects assessment mode, not workflow mode.

## Must Create a Workflow

Create a durable workflow and its discovery locator when any of these are true:

- the task needs two or more stages;
- the task needs cross-skill or sub-agent handoff;
- the task changes canonical source-of-truth rules;
- the task reorganizes `.ai/`, `.dev/`, `.agents/`, `.claude/`, or wrapper routing;
- the task affects future agent behavior;
- the task needs plan, review, or task status artifacts;
- the task involves document governance, source-of-truth cleanup, or context boundary changes;
- the task will likely touch five or more files;
- the user uses wording such as "workflow", "規劃", "整理", "重構", "標準化", "治理", or "拆分" for repo-wide documentation or context work.

## Direct Mode Is Enough

Direct mode is acceptable when all of these are true:

- the change is small and local;
- only one skill is needed;
- no durable decision trail is required;
- no canonical rule or source-of-truth boundary changes;
- no task status needs to be preserved;
- validation can be completed in the same turn.

Transient read-only analysis is also direct mode even when it is multi-stage or uses sub-agents, provided that all of these are true:

- the result is returned only in the conversation;
- no durable report or workflow artifact is written to the repository;
- no repository file is mutated;
- no finding is remediated.

## Assessment Mode

Use assessment mode when all of these are true:

- the requested result is a durable audit, large code review, architecture assessment, or similar observation;
- the assessed surfaces remain read-only;
- remediation or implementation is not authorized;
- task-level execution tracking is not required beyond the assessment locator's draft resume checkpoint.

Follow `.dev/standards/ASSESSMENT-ARTIFACT-POLICY.md`. Create a dedicated
assessment branch before writing `.dev/assessments/<assessment-id>/`, but do not
create a workflow locator solely because the report is durable. Commits contain
only assessment-owned artifacts and required assessment index updates.

If remediation is authorized later, create a new workflow and reference the
assessment and selected finding IDs. If assessment and remediation are requested
together, use workflow mode for execution while keeping the assessment report
under `.dev/assessments/`.

## Workflow Artifacts

When workflow mode is used:

1. Start from the intended base branch, normally `main`.
2. Create or switch to a dedicated workflow branch before creating workflow artifacts or making material task changes.
3. Then create the workflow locator and skill-owned artifacts.

Branch naming, checkpoint merge, continuation branch, push, and `--no-ff` details are defined by `.dev/TEAM-GIT-FLOW-RULES.MD`.

```text
.dev/workflows/<workflow-id>/
  workflow.yaml
```

- Follow `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md` for discovery, full-date IDs, timestamps, artifact roots, and minimum task metadata.
- Use the workflow-owning skill's templates for its plan, tasks, reports, and domain-specific layout.
- Default the artifact root to `.dev/workflows/<workflow-id>/`; a skill may declare another repository-relative root while retaining the locator above.
- Do not assume every workflow has `review-report.md` or the same task/report structure.
- Do not create a workflow directly on `main`. Historical workflows created before this rule are not retroactively rewritten, but must use a dedicated continuation branch before resuming material work.

## Task Status Rule

Each task JSON should move through:

```text
pending -> in_progress -> completed
```

Use `deferred` only when the task is intentionally postponed and the workflow plan or task results explain why.

## Commit Rule

Workflow stages should follow `.dev/standards/GIT-COMMIT-POLICY.md`. Commit after a stage or coherent task batch completes and validation has passed.

Merging or pushing an incomplete workflow is a checkpoint handoff, not workflow completion. Keep the workflow and unfinished tasks active. Resume a push-only handoff from the pushed branch; after a checkpoint merge, create the next continuation branch from the updated target as defined by `.dev/TEAM-GIT-FLOW-RULES.MD`.

## Workflow Closing Checklist

Before sending a final response in workflow mode, the agent must verify all of the following:

- workflow plan and task artifacts reflect the completed or deferred state;
- required validation has passed, or skipped validation is explicitly recorded with a reason;
- `.dev/standards/GIT-COMMIT-POLICY.md` has been checked for commit requirements;
- when the commit policy requires a commit, the commit has been created before claiming completion;
- when no commit is created, the final response cites the exact policy exception that applies.
- the workflow was not marked complete merely because its branch was merged or pushed as a checkpoint;
- any requested merge used `--no-ff` unless the user explicitly selected another strategy.

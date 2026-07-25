# AI Context Audit Workflow

> Historical compatibility template only. New durable read-only audits use a
> standalone assessment locator under `.dev/assessments/` and the current
> `ai-context-auditor` report template. The current auditor must not create this
> workflow model.

## Template Metadata

- `template_id`: `ai-context-auditor-workflow-plan`
- `template_version`: `1.1.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-11T00:22:30+08:00`

## Workflow Metadata

- `workflow_id`: `<YYYY-MM-DD-topic[-NN]>`
- `workflow_kind`: `ai-context-audit`
- `owner_skill`: `ai-context-auditor`
- `branch`: `<runtime-prefix>/<workflow-id>`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `in_progress`
- `artifact_root`: `<artifact-root>`
- `created_at`: `<ISO-8601-with-offset>`
- `updated_at`: `<ISO-8601-with-offset>`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-workflow-plan-template.md`
- `template_version`: `1.1.0`

## Objective And Scope

- Audit reason:
- Included AI context surfaces:
- Excluded source, test, generated, and dependency surfaces:
- Previous report:
- Completion criteria:

## Artifact Contract

- Baseline audit: `<artifact-root>/reports/01-audit-report.md`
- Post-remediation audit, when requested by governance: `<artifact-root>/reports/03-post-remediation-audit-report.md`
- Tasks: `<artifact-root>/tasks/`

## Audit Stages

1. Intake and evidence boundary
2. Independent baseline
3. Repository-aware assessment
4. Comparison and evidence verification
5. Report persistence and governance handoff

## Read-Only Contract

- Do not remediate findings.
- Do not inspect product source or test implementation.
- Writing this workflow's metadata, task state, and reports does not authorize other repository changes.

## Resume Checkpoint

- Last completed action:
- Current audit stage:
- Exact next action:
- Evidence already collected:
- Git state:
- Branch history and checkpoint handoffs:
- Blockers:

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 |  |  |  |  |  |  |  |  |

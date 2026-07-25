# Software Development Orchestrator Plan

## Template Metadata

- `template_id`: `software-development-orchestrator/development-workflow-plan`
- `template_version`: `1.3.0`
- `template_created_at`: `2026-07-10T18:25:11+08:00`
- `template_updated_at`: `2026-07-24T08:10:00+08:00`

## Workflow Metadata

- `workflow_id`: `<YYYY-MM-DD-topic[-NN]>`
- `plan_id`: `development-plan-<YYYY-MM-DD-topic[-NN]>`
- `owner_skill`: `software-development-orchestrator`
- `branch`: `<runtime-prefix>/<workflow-id>`
- `base_branch`: `main`
- `branch_segment`: `1`
- `status`: `draft | active | completed | superseded`
- `created_at`: `<ISO-8601 timestamp with UTC offset>`
- `updated_at`: `<ISO-8601 timestamp with UTC offset>`
- `template_source`: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- `template_version`: `1.3.0`
- `workflow_locator`: `.dev/workflows/<workflow-id>/workflow.yaml`
- `artifact_root`: `<repository-relative artifact root; default .dev/workflows/<workflow-id>/>`

## Development Objective

- Product or software outcome:
- Current lifecycle entry point:
- User constraints:
- Non-goals:

## Inputs

- Requirements:
- Specifications:
- Architecture decisions:
- Existing implementation or tests:

## Development Stages

### Stage 1

- `stage_id`:
- Goal:
- Capability slot:
- Owner skill:
- Scope:
- Non-goals:
- Dependencies:
- Validation:
- Commit checkpoint:

## Approval Gates

| Transition | Status | Authorization Source | Pending Decision |
| --- | --- | --- | --- |
| requirement/design/specification -> implementation | `awaiting-approval | approved | not-required` |  |  |

Do not create or execute implementation work while the applicable transition
is `awaiting-approval`.

## Validation Strategy

- Requirement/spec traceability:
- Architecture validation:
- Test and implementation validation:
- Review/compliance gates:

## Test Execution Contract

- Provider: `target-profile-commands | evaluated-external-skill | fallback-contract`
- Target-owned working directory:
- Target-owned commands:
- Prerequisites and environment boundary:
- Target policy:
- Default selected levels: `unit`, `integration`
- Conditional selected levels and activation source:

| Level | Outcome | Evidence | Deferral Owner / Follow-up |
| --- | --- | --- | --- |
| unit | `passed | failed | blocked-by-environment | not-applicable | deferred-with-owner` |  |  |
| integration | `passed | failed | blocked-by-environment | not-applicable | deferred-with-owner` |  |  |

## Spec Compliance Selection

- Selected: `yes | no`
- Activation source:
- Outcome: `100-percent-pass | failed-closed | not-applicable`
- Coverage and evidence:

## Progress And Handoff

- Current stage:
- Completed stages:
- Deferred stages and reasons:
- Open decisions:
- Continuation instructions:
- Target policy references:
- Registered handoff checkpoint:
- Branch history and checkpoint handoffs:

## Branch Lifecycle

| Segment | Branch | Base | Checkpoint Type | Commit | Remote / Target | Recorded At | Reason | Resume Branch / Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 |  |  |  |  |  |  |  |  |

## Completion Summary

- Outcome:
- Changed artifacts:
- Approved requirement/specification evidence:
- Implementation completion evidence:
- Required test outcomes:
- Selected compliance evidence:
- Review disposition:
- Validation evidence:
- Workflow task state:
- Commits:
- Branch / checkpoint / handoff evidence:
- Residual risks:

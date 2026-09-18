# AI Context Audit Report

## Template Metadata

- `template_id`: `ai-context-auditor-report`
- `template_version`: `2.1.0`
- `created_at`: `2026-07-10T18:22:49+08:00`
- `updated_at`: `2026-07-15T08:39:00+08:00`

## Metadata

- `assessment_id`: `<ASM-YYYYMMDD-NNN>`
- `assessment_type`: `ai-context-audit | ai-context-verification`
- `owner_skill`: `ai-context-auditor`
- `status`: `draft | final`
- `audit_date`:
- `created_at`: `<ISO-8601-with-offset>`
- `updated_at`: `<ISO-8601-with-offset>`
- `template_source`: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- `template_version`: `2.1.0`
- `repository`:
- `subject_branch`:
- `subject_commit`:
- `previous_assessment`:
- `workflow_refs`:

## Executive Summary

- Overall assessment:
- Overall score: `/10` or `N/A`
- Decision: `healthy | healthy-with-followups | remediation-recommended | critical-remediation-required`
- Primary strengths:
- Primary risks:

## Scope

### Included AI Context Surfaces

-
### Default Exclusions

- `src/**`
- `tests/**`, `test/**`
- product implementation trees
- generated and dependency trees

### Additional Exclusions

-

### Code Review Handoff

- Requested: `yes | no`
- Paths not scanned:
- Recommended skill:

## Methodology And Evidence

### Pass A: Independent Baseline

- Evidence used:
- Checks performed:

### Pass B: Repository-Aware Skill Review

- Policies and skills used:
- Checks performed:

### Delegation

- Sub-agents used:
- Assigned surfaces:

### Discovery Accelerators

| Tool / generated view | Source revision or input digest | Freshness / dirty state | Scope and exclusions | Unsupported relationships | File-backed fallback |
| --- | --- | --- | --- | --- | --- |
| None / not applicable |  |  |  |  |  |

## Repository Context Inventory

| Surface | Files / Size | Audience | Scope | State | Notes |
| --- | ---: | --- | --- | --- | --- |
| Root entries |  |  |  |  |  |
| `.ai/**` |  |  |  |  |  |
| `.dev/**` |  |  |  |  |  |
| Runtime wrappers |  |  |  |  |  |

## Strengths

1.

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation | Owner / Next Skill |
| --- | --- | --- | --- | --- | --- | --- |
| AIC-001 |  |  |  |  |  |  |

## Baseline And Skill Comparison

### Confirmed

-

### Added By Repository-Aware Review

-

### Downgraded Or Deferred

-

### Overturned

-

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Git state |  |  |
| Registry and wrapper parity |  |  |
| Path and reference checks |  |  |
| Schema / structured file parse |  |  |
| Repository context checks |  |  |

### Skipped Validation

-

## Recommended Action Order

1.

## Deferred Items

-

## Appendix

### Commands Run

```text
<commands>
```

### Notes

-

## Lifecycle Handoff

- Assessment path: `.dev/assessments/<assessment-id>/report.md`
- Stable finding references: `<assessment-id>#<finding-id>`
- Remediation owner: `ai-context-governance`
- Related remediation workflow:
- Verification assessment:
- Remediation intentionally not performed by this skill: `yes`

# Code Review Assessment Report

## Template Metadata

- `template_id`: `code-review-assessment-report`
- `template_version`: `1.1.0`
- `created_at`: `2026-07-13T23:22:03+08:00`
- `updated_at`: `2026-09-12T11:58:27+08:00`

## Metadata

- `assessment_id`: `<ASM-YYYYMMDD-HH-xxx>`
- `assessment_type`: `code-review | code-review-verification`
- `owner_skill`: `code-reviewer`
- `status`: `draft | final`
- `created_at`: `<ISO-8601-with-offset>`
- `updated_at`: `<ISO-8601-with-offset>`
- `template_source`: `.ai/assets/skills/code-reviewer/templates/code-review-assessment-report-template.md`
- `template_version`: `1.1.0`
- `repository`:
- `subject_branch`:
- `subject_commit`: `<40-character-Git-SHA>`
- `previous_assessment`:
- `workflow_refs`:

## Executive Summary

- Optional score and target-requested rubric: `/10` or `N/A`
- Decision: `pass | pass-with-followups | remediation-recommended | blocking-findings`
- Highest severity:
- Primary strengths:
- Primary risks:

## Review Scope

### Included

-

### Excluded

-

### Subject State

- Reviewed committed revision:
- Uncommitted changes present: `yes | no`
- Limitation if uncommitted scope was considered:

## Methodology And Evidence

- Common route and extensions selected:
- Target technology/architecture selection evidence:
- Unavailable specialist coverage and required gates:
- File types and checklists selected:
- Repository standards loaded:
- Analyzer, architecture-test, or test evidence:
- Manual reasoning performed:
- Evidence limitations:

## Scorecard

| Area | Score | Evidence / Notes |
| --- | ---: | --- |
| Behavior and contract compatibility |  |  |
| Adopted architecture and dependency boundaries |  |  |
| Implementation correctness |  |  |
| Test design and coverage |  |  |
| Maintainability |  |  |

## Findings

| ID | Severity | Level | Location | Finding | Evidence | Recommendation | Next Skill |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CR-001 | `CRITICAL | MUST FIX | SHOULD FIX` | `architecture | code | test` |  |  |  |  |  |

Durable reference form: `<assessment-id>#<finding-id>`.

## Validation

| Check | Result | Evidence / Notes |
| --- | --- | --- |
| Git revision and worktree state |  |  |
| Narrowest meaningful tests |  |  |
| Analyzer or architecture checks |  |  |
| Checklist comparison |  |  |

### Skipped Validation

-

## Recommended Handoff

- Target architecture decision needed: `yes | no`
- Recommended owner skill:
- Candidate finding references:
- Suggested grouping into workflow tasks:
- Remediation intentionally not performed by `code-reviewer`: `yes`

## Lifecycle

- Assessment path: `.dev/assessments/<assessment-id>/report.md`
- Related remediation workflow:
- Verification assessment:
- Supersedes:

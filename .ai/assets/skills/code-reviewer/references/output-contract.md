# Code Reviewer Output Contract

Canonical ownership rule: `ASSESSMENT-ARTIFACT-001`.

This contract separates review observations from authorized implementation.

## Transient Direct Mode

When the user does not ask to persist the review, return findings in the
conversation. Do not create a branch, assessment, workflow, report, or commit.
The review remains read-only even when it uses tests or analyzers as evidence.

## Standalone Durable Assessment Mode

When the user asks to save a large or formal code review without authorizing
remediation, allocate an `ASM-YYYYMMDD-NNN` assessment ID and create the locator
from `.dev/assessments/templates/assessment-locator-template.yaml`.

Create the report from:

```text
.ai/assets/skills/code-reviewer/templates/code-review-assessment-report-template.md
```

Store it at `.dev/assessments/<assessment-id>/report.md`, update
`.dev/assessments/INDEX.MD`, and follow
`.dev/standards/ASSESSMENT-ARTIFACT-POLICY.md`. Pin
`subject_ref.commit` to the exact 40-character Git revision reviewed. A dirty
worktree may be reviewed only when the report explicitly records that limitation
and identifies uncommitted scope; prefer a committed subject for durable claims.

Use `CR-001`, `CR-002`, and so on inside the report. The durable external
reference is `<assessment-id>#<finding-id>`, for example
`ASM-20260713-001#CR-001`. Final finding IDs are immutable.

## Development Workflow Participation

When review and remediation are authorized together, create the assessment on
the active development workflow branch and relate it to that workflow. Do not
open a competing assessment branch. The assessment records observed state; the
workflow owns task selection, implementation, validation, and closeout.

A post-remediation review is a new assessment related to the baseline. It does
not rewrite the original report. `code-reviewer` may verify convergence but must
not implement fixes, define target architecture, or silently expand review scope.

## Required Report Content

Include assessment metadata, reviewed revision, included and excluded paths,
checklist selection, evidence and limitations, scored summary, severity-ranked
architecture- and code-level findings, validation performed or skipped, and
handoff recommendations. Categorize actionable issues using the repository's
`CRITICAL`, `MUST FIX`, and `SHOULD FIX` review severities.

The final response states whether the result was transient or durable, the
reviewed revision, highest-priority findings, skipped validation, and the
recommended next skill. Durable mode also returns the assessment ID and path.

# AI Context Auditor Output Contract

Canonical ownership rule: `ASSESSMENT-ARTIFACT-001`.

This contract has three routing cases and two report surfaces.

## Transient Direct Mode

When the user does not ask to persist the result, return the assessment in the conversation. Do not create a branch, workflow artifact, report file, or commit. Multiple passes and sub-agent analysis do not change this mode. Do not mutate audited context or remediate findings.

## Standalone Durable Assessment Mode

When the user asks to save, persist, land, or retain the audit without authorizing remediation, allocate an assessment ID and create the locator from:

```text
.dev/assessments/templates/assessment-locator-template.yaml
```

Create the durable Markdown report from:

```text
.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md
```

Destination:

```text
.dev/assessments/<ASM-YYYYMMDD-NNN>/report.md
```

Use `.dev/assessments/<assessment-id>/assessment.yaml` as the stable locator and update `.dev/assessments/INDEX.MD`. Do not create workflow artifacts solely because the assessment is persisted.

A standalone assessment uses its own dedicated assessment branch. An audit stage inside a governance-owned lifecycle uses the governance workflow branch and must not open a competing assessment branch. Keep draft resume metadata current before any push or merge handoff.

## Governance Workflow Participation

When remediation is already authorized, create the baseline or verification
assessment under `.dev/assessments/` on the active governance workflow branch.
Reference the workflow from the assessment locator and reference the assessment
and selected finding IDs from workflow tasks. The auditor remains read-only and
does not author remediation conclusions.

The report must include metadata and scope, explicit code exclusions, methodology and evidence, both audit passes, their comparison, strengths, severity-ranked findings, validation and skipped checks, deferred items and code-review handoffs, and prioritized actions.

Include ISO 8601 `created_at` and `updated_at` values with an explicit offset plus locator and report template sources and versions. Pin the assessed subject commit. Do not mark the assessment final while high-severity claims lack file-backed evidence.

The final response must return the overall assessment, highest-priority findings, scope exclusions, validation summary, recommended next skill, and whether remediation was intentionally not performed. Include the assessment ID and report path only in durable mode; in transient mode state that no repository artifact was created.

If source-code review was requested, return the handoff instead of an AI context finding about unread code.

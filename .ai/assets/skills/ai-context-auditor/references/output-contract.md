# AI Context Auditor Output Contract

This contract has two output modes.

## Transient Direct Mode

When the user does not ask to persist the result, return the assessment in the conversation. Do not create a branch, workflow artifact, report file, or commit. Multiple passes and sub-agent analysis do not change this mode. Do not mutate audited context or remediate findings.

## Durable Report Mode

When the user asks to save, persist, land, or retain the audit in the repository, create or update a durable Markdown report from:

```text
.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md
```

Baseline destination:

```text
<artifact-root>/reports/01-audit-report.md
```

Post-remediation destination:

```text
<artifact-root>/reports/03-post-remediation-audit-report.md
```

Use `.dev/workflows/<YYYY-MM-DD-topic[-NN]>/workflow.yaml` as the stable locator. For audit-only workflows, initialize the locator, plan, and task from the templates owned by this skill. For a governance-owned lifecycle, update only the auditor-owned report and audit task fields authorized by that workflow.

An audit-only workflow uses its own dedicated branch. An audit stage inside a governance-owned lifecycle uses the governance workflow branch and must not open a competing workflow branch. Report push/merge handoffs separately from final audit completion.

The report must include metadata and scope, explicit code exclusions, methodology and evidence, both audit passes, their comparison, strengths, severity-ranked findings, validation and skipped checks, deferred items and code-review handoffs, and prioritized actions.

Include ISO 8601 `created_at` and `updated_at` values with an explicit offset plus `template_source` and `template_version`. Do not mark the report final while high-severity claims lack file-backed evidence.

The final response must return the overall assessment, highest-priority findings, scope exclusions, validation summary, recommended next skill, and whether remediation was intentionally not performed. Include a report path only in durable mode; in transient mode state that no repository artifact was created.

If source-code review was requested, return the handoff instead of an AI context finding about unread code.

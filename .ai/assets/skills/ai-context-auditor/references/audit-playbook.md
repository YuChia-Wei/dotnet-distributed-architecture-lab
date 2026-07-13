# AI Context Audit Playbook

## 1. Intake And Evidence Boundary

Record the repository identity, audit reason, requested focus, included context roots, excluded code/generated surfaces, previous report, and whether bounded sub-agent delegation is useful. First classify the output as transient or durable.

- Transient read-only analysis returns results only in the conversation. It may use multiple passes or sub-agents in direct mode, but writes no repository artifact, mutates no repository file, and performs no remediation.
- Durable report-only audit applies when the user asks to save, persist, land, or retain the report in the repository. It requires the skill-owned workflow artifacts and dedicated branch, while audited surfaces remain read-only.
- Authorized remediation is not an auditor mode; hand it to `ai-context-governance` for the normal remediation lifecycle.

When the audit needs a durable workflow, create or switch to its dedicated branch before writing the locator, task, or report. Record `branch` and `base_branch`. Follow `.dev/TEAM-GIT-FLOW-RULES.MD` for push handoff, checkpoint merge, continuation, and default `--no-ff` behavior; keep pre-completion checkpoints active.

Read deeper `AGENTS.*` files before auditing a governed subtree. Keep the audited context read-only. If remediation is separately authorized, hand the findings to `ai-context-governance`; do not expand the auditor into an implementer.

## 2. Pass A: Independent Baseline

Assess the repository using general knowledge before treating its own governance policies as the rubric. Review:

- repository identity and truth boundaries;
- information architecture and navigation;
- canonical ownership and duplication;
- instruction clarity, precedence, and actionability;
- active versus example, historical, generated, and planned content;
- runtime wrapper and registry relationships;
- schema and template consistency;
- language and audience consistency;
- validation integrity and fail-open behavior;
- scale, cognitive load, lifecycle, and portability.

Capture strengths as well as defects. Do not read product code to validate architecture or coding claims.

## 3. Pass B: Repository-Aware Assessment

After the baseline is recorded, apply repository-specific policies and relevant skills. For this repository, use `ai-context-governance` for audience, scope, language, placement, routing, wrapper rules, and AI context audit lifecycle handoff. Read the active workflow's skill-owned template contract for artifact, validation, and handoff rules.

Check whether the repository follows its own declared contracts. Do not allow a policy assertion to erase contradictory file-backed evidence.

## 4. Parallel Audit Pattern

When the context is large and sub-agents are available, use bounded read-only tasks for structure/navigation, content truth/rule strength/language, and runtime wrappers/schemas/scripts/validation. Tell each worker the same exclusions. The main agent verifies high-severity evidence, resolves duplicates, compares both passes, and owns the final report.

## 5. Finding Rules

| Severity | Meaning |
| --- | --- |
| `CRITICAL` | The context can directly cause unsafe, destructive, or broadly incorrect agent behavior. |
| `HIGH` | Active rules conflict, canonical truth is ambiguous, or validation can materially mislead execution. |
| `MEDIUM` | Navigation, maintenance, lifecycle, portability, or policy drift increases recurring error risk. |
| `LOW` | Local clarity, consistency, or hygiene issue with limited behavioral impact. |

Each finding must contain evidence, impact, recommendation, and an appropriate owner or next skill. Separate active defects from historical references, accepted exceptions, and items needing a domain decision.

## 6. Validation

Prefer deterministic read-only checks: explicit `rg --files --hidden` include/exclude globs, path existence, registry comparison, structured-file parsing, Markdown/reference checks, wrapper-to-canonical checks, targeted context validation scripts, and Git state checks.

Record exact commands and results. A warning-only or skipped gate is not equivalent to a passing semantic validation.

## 7. Comparison And Persistence

Compare confirmed findings, findings added by repo policies, downgraded or deferred findings, overturned findings, and residual uncertainty.

For durable mode, create the report from the canonical template and use a full-date workflow id. In transient mode, present the same evidence discipline and comparison in the conversation without creating repository artifacts.

```text
.dev/workflows/<YYYY-MM-DD-ai-context-audit[-NN]>/
```

Use `YYYY-MM-DD-topic[-NN]`; if the base id exists, append `-02`, `-03`, and so on. Keep `.dev/workflows/<workflow-id>/workflow.yaml` as the locator even when `artifact_root` points elsewhere.

Write the initial audit to `<artifact-root>/reports/01-audit-report.md`. When `ai-context-governance` requests independent verification after remediation, write `<artifact-root>/reports/03-post-remediation-audit-report.md`. Never replace the baseline report.

Set `created_at` and `updated_at` using ISO 8601 with an explicit offset. Preserve `created_at`; change `updated_at` whenever the generated artifact changes. Record `template_source` and `template_version` in every generated workflow artifact.

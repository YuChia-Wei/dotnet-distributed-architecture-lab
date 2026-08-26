# AI Context Audit Playbook

Rule IDs: `AICTX-EVIDENCE-001`

## 1. Intake And Evidence Boundary

Record the repository identity, audit reason, requested focus, included context roots, excluded code/generated surfaces, previous report, and whether bounded sub-agent delegation is useful. First classify the output as transient or durable.

- Transient read-only analysis returns results only in the conversation. It may use multiple passes or sub-agents in direct mode, but writes no repository artifact, mutates no repository file, and performs no remediation.
- Durable assessment mode applies when the user asks to save, persist, land, or retain the report in the repository without authorizing remediation. It requires the repository assessment locator, auditor-owned report, assessment index update, and dedicated assessment branch, while audited surfaces remain read-only.
- Authorized remediation is not an auditor mode; hand it to `ai-context-governance` for the normal remediation lifecycle.

For a standalone durable audit, allocate an `ASM-YYYYMMDD-NNN` ID and create or switch to the dedicated assessment branch before writing `assessment.yaml` or `report.md`. Record the assessed subject revision separately from the artifact branch. Follow `.dev/standards/ASSESSMENT-ARTIFACT-POLICY.md` and `.dev/TEAM-GIT-FLOW-RULES.MD`. When the audit is part of an authorized governance workflow, use the workflow branch and create the assessment under `.dev/assessments/` without opening a competing branch.

Read deeper `AGENTS.*` files before auditing a governed subtree. Keep the audited context read-only. If remediation is separately authorized, hand the findings to `ai-context-governance`; do not expand the auditor into an implementer.

Optional indexes, code graphs, IDE indexes, MCP servers, and semantic search may
accelerate discovery, but they are candidate generators only. Do not make this
skill depend on one tool or accept an absence, inventory, or relationship claim
from tool output alone. Follow the canonical quick fallback checks in
`.dev/standards/AI-CONTEXT-BOUNDARY.md#tool-neutral-evidence-boundary` and record
the accelerator's freshness, scope, exclusions, and unsupported relationship
classes when they affect the audit.

If a retained generated inventory or index is used, verify that it declares
the generator, generation time, source revision or input digest, scope, and
exclusions. Record the comparison in the report's Discovery Accelerators table.
Missing or stale provenance downgrades the artifact to a discovery hint; it
does not establish absence or completeness.

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

After the baseline is recorded, apply repository-specific policies and relevant skills. For this repository, use `ai-context-governance` for audience, scope, language, placement, routing, wrapper rules, and AI context audit lifecycle handoff. Read the assessment policy and, when remediation is already authorized, the active workflow's skill-owned template contract.

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

When an accelerator omits a relevant root such as `.claude/`, enumerate that
root through Git and inspect it directly. When a graph does not model Markdown
links, search the literal link or target in tracked Markdown and resolve the
target relative to its source file. Treat missing broad link validation as an
explicit coverage gap, not as a passing relationship check.

## 7. Comparison And Persistence

Compare confirmed findings, findings added by repo policies, downgraded or deferred findings, overturned findings, and residual uncertainty.

For durable mode, create the locator from the repository assessment template and the report from the auditor template. In transient mode, present the same evidence discipline and comparison in the conversation without creating repository artifacts.

```text
.dev/assessments/<ASM-YYYYMMDD-NNN>/
  assessment.yaml
  report.md
```

Use the next unused assessment sequence for the local creation date. Keep the assessment ID, directory, locator, report metadata, commit subject, and `Assessment-Id` trailer synchronized.

Write both baseline audits and independent post-remediation verification as separate assessments. A verification assessment links the baseline assessment and governance workflow; it never replaces the baseline report.

Set `created_at` and `updated_at` using ISO 8601 with an explicit offset. Preserve `created_at`; change `updated_at` whenever the assessment content, status, relationship, or resume state changes. Record locator and report template sources and versions, update `.dev/assessments/INDEX.MD`, then run `validate-assessment-artifacts.py`.

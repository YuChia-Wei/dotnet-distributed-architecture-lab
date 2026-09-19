---
name: code-reviewer
description: Review code and implementation guidance through a technology-neutral
  reasoning core, selected technology extensions and target-owned rules. Return evidence-backed
  findings without implementing fixes or defining target architecture.
---

# Code Reviewer

This runtime execution entry is generated. Do not edit it by hand.

## Authority and provenance

- Execution authority: `.ai/assets/skills/code-reviewer/skill.yaml` `runtime_entry`.
- Runtime frontmatter is discovery metadata generated from canonical `asset_id` and `purpose`; it does not add execution authority.
- Generator: `.ai/scripts/generate-runtime-skill-entries.py`; canonical source SHA-256: `d3779886ef5f7a26851f98eeb120d153d3fb7df0de61570b29898d1de2b0d52e`.
- Regenerate after canonical changes, then verify exact parity with `python .ai/scripts/generate-runtime-skill-entries.py --root <absolute-repository-root> --check`.
- This entry does not promise zero additional reads. Load the listed canonical material only when its condition applies.

## Use this entry when

Use for a bounded code or implementation-guidance review that returns evidence-backed findings and coverage limitations without applying remediation.

## Execute

1. Identify the reviewed subject, intended behavior, target authority, included and excluded paths, and whether the review is transient or explicitly durable.
2. Read the common review route first. Select only target-selected installed extensions and matching reviewed partitions; do not infer a profile from a file suffix.
3. Before judging catalog rules, select one applicability mode declared by the effective-rule-consumption authority and consume every applicable freshness-verified effective-rule packet. Preserve missing specialist coverage and unresolved authority as limitations.
4. Review behavior, contracts, boundaries, compatibility, failures, tests, and relevant risks within the selected routes. Keep the review read-only and distinguish findings from uncertainty.
5. Evaluate each applicable role binding. In a routine direct review, record only material applicable roles and state that unselected roles were not applicable; use full per-role execution records only for a terminal, high-risk, or external acceptance path.
6. Load the output contract only when findings are ready to format or persistence is requested.

## Canonical capability slots

- Generated from `.ai/assets/skills/code-reviewer/skill.yaml` `capability_slots`: `review`.

## Effective-rule preflight

- Select only an applicability mode declared by this canonical payload: `initialized-target`.
- When `initialized-target`, before the resolver invocation, inspect only `.dev/ai-context/effective-rules.yaml` routing selector inventory.
- For each task partition, select an existing exact tuple of `capability`, `execution_mode`, `technology_profile`, `file_type`; do not derive selectors from this skill ID, an action label, or a file suffix.
- If no exact existing tuple is available, preserve canonical unresolved outcome `stop-applicable-action`; do not use aliases or default routes.
- Use the request-authorized effective-rule resolver invocation. Run `.ai/scripts/resolve-effective-rule-packet.py --help` only when its supported interface is needed.

## Canonical role bindings

- Generated from `.ai/assets/skills/code-reviewer/skill.yaml` `role_bindings`; this selection metadata does not execute, delegate, or replace a canonical role contract.
- `code-review-sub-agent` — `.ai/assets/skills/code-reviewer/roles/code-review-sub-agent/sub-agent.yaml`
  - Binding kind: `primary`
  - Applies when: A bounded code or implementation-guidance review scope is selected, regardless of technology.
  - Load obligation: `mandatory-when-applicable`
- `aggregate-code-review-sub-agent` — `.ai/assets/skills/code-reviewer/roles/aggregate-code-review-sub-agent/sub-agent.yaml`
  - Binding kind: `conditional`
  - Applies when: The target adopts aggregate or event-sourcing concepts for the selected scope, or domain-invariant behavior needs bounded review.
  - Load obligation: `mandatory-when-applicable`
- `controller-code-review-sub-agent` — `.ai/assets/skills/code-reviewer/roles/controller-code-review-sub-agent/sub-agent.yaml`
  - Binding kind: `conditional`
  - Applies when: The selected scope includes an HTTP controller, endpoint, transport-data boundary or HTTP contract.
  - Load obligation: `mandatory-when-applicable`
- `reactor-code-review-sub-agent` — `.ai/assets/skills/code-reviewer/roles/reactor-code-review-sub-agent/sub-agent.yaml`
  - Binding kind: `conditional`
  - Applies when: The selected scope includes event handling, handler registration or adopted cross-aggregate integration boundaries.
  - Load obligation: `mandatory-when-applicable`

## Conditional expansion

- When: Always before reviewing.
  - Read: `.ai/assets/skills/code-reviewer/references/review-routing.yaml`
  - Why: The common route always applies and controls selective extension loading.
- When: After common and extension selection.
  - Read: `.ai/assets/skills/code-reviewer/references/core-review-playbook.md`, `the selected extension contracts and target-owned rules`
  - Why: Review only the common and selected specialist semantics; report unavailable specialist coverage.
- When: Before judging applicable catalog rules.
  - Use: Run `.ai/scripts/resolve-effective-rule-packet.py --help` only when its supported interface is needed; otherwise use the request-authorized resolver invocation.
  - Read: `the selected freshness-verified task-scoped effective-rule packet`
  - Why: Consume fresh task-scoped effective-rule evidence and never replace it with a framework default.
- When: A material role binding applies to the bounded review scope, or the review is terminal, high-risk, or external.
  - Read: `.ai/assets/skills/code-reviewer/references/role-execution.md`, `the applicable canonical role manifest and every reference it declares`
  - Why: Use proportionate role evidence without transferring finding ownership.
- When: Findings are ready to format or a durable assessment is explicitly requested.
  - Read: `.ai/assets/skills/code-reviewer/references/output-contract.md`, `.ai/assets/skills/code-reviewer/templates/code-review-assessment-report-template.md`
  - Why: Select transient or durable output without creating an unrequested assessment.

## Stop or hand off

- Do not implement fixes, define target architecture, or output a staged refactoring plan. Route remediation to the appropriate authorized owner.
- Stop the affected specialist rule check when target authority, selected extension, or effective-rule packet is unresolved; report the coverage limitation instead of silently choosing a fallback.
- Do not treat tests, analyzers, compatibility summaries, or role prompts as replacements for review reasoning or canonical rule ownership.

## Return

- transient findings or an explicitly requested durable assessment
- reviewed scope, selected routes, evidence, coverage, and limitations
- severity-ranked findings with trigger, impact, supporting evidence, and uncertainty
- read-only handoff recommendations and proportionate role execution evidence

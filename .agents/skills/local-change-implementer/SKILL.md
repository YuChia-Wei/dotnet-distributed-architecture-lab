---
name: local-change-implementer
description: Execute one local technical target and operation, including direct call
  sites and immediate tests in the allowed radius. File count alone does not expand
  scope; a private implementation helper type may remain local only when its semantic
  impact stays inside the accepted target and radius.
---

# Local Change Implementer

This runtime execution entry is generated. Do not edit it by hand.

## Authority and provenance

- Execution authority: `.ai/assets/skills/local-change-implementer/skill.yaml` `runtime_entry`.
- Runtime frontmatter is discovery metadata generated from canonical `asset_id` and `purpose`; it does not add execution authority.
- Generator: `.ai/scripts/generate-runtime-skill-entries.py`; canonical source SHA-256: `91229555dd92a80c584db93cf7fe23aea48f612f95798901b34e1e76ef7d52e4`.
- Regenerate after canonical changes, then verify exact parity with `python .ai/scripts/generate-runtime-skill-entries.py --root <absolute-repository-root> --check`.
- This entry does not promise zero additional reads. Load the listed canonical material only when its condition applies.

## Use this entry when

Use for one accepted local technical target and operation, including direct call sites and immediate tests inside its allowed radius.

## Execute

1. Confirm the primary target, one local operation, accepted behavior, direct call sites, immediate tests, and allowed dependency radius. Judge scope by semantic impact, not file count.
2. Select one applicability mode declared by the effective-rule-consumption authority, then consume its freshness-verified task-scoped effective-rule packet before applying applicable catalog or profile rules. Stop if that route is unresolved.
3. Apply the smallest coherent local change and update only its direct usage sites and immediate tests when necessary. Preserve existing authorization; do not widen it.
4. Run the narrowest meaningful validation for the changed behavior and report compatibility, touched radius, and any prevented expansion.

## Canonical capability slots

- Generated from `.ai/assets/skills/local-change-implementer/skill.yaml` `capability_slots`: `local-change`.

## Effective-rule preflight

- Select only an applicability mode declared by this canonical payload: `initialized-target`.
- When `initialized-target`, before the resolver invocation, inspect only `.dev/ai-context/effective-rules.yaml` routing selector inventory.
- For each task partition, select an existing exact tuple of `capability`, `execution_mode`, `technology_profile`, `file_type`; do not derive selectors from this skill ID, an action label, or a file suffix.
- If no exact existing tuple is available, preserve canonical unresolved outcome `stop-applicable-action`; do not use aliases or default routes.
- Use the request-authorized effective-rule resolver invocation. Run `.ai/scripts/resolve-effective-rule-packet.py --help` only when its supported interface is needed.

## Conditional expansion

- When: Always before choosing the implementation owner.
  - Read: `.ai/assets/shared/IMPLEMENTATION-SCOPE-ROUTING-CONTRACT.md`
  - Why: Classify the change by target, radius, and semantic impact.
- When: Before an applicable catalog or profile rule is judged.
  - Use: Run `.ai/scripts/resolve-effective-rule-packet.py --help` only when its supported interface is needed; otherwise use the request-authorized resolver invocation.
  - Read: `the selected freshness-verified task-scoped effective-rule packet`
  - Why: Select the applicability mode explicitly and consume only fresh task-scoped effective-rule evidence.
- When: The local operation, direct-call-site radius, or handoff boundary needs detail.
  - Read: `.ai/assets/skills/local-change-implementer/references/allowed-operations.md`, `.ai/assets/skills/local-change-implementer/references/execution-rules.md`, `.ai/assets/skills/local-change-implementer/references/skill-boundaries.md`
  - Why: Use the canonical local-operation and handoff boundaries without inventing a broader scope.

## Stop or hand off

- Route to `slice-implementer` when the change requires a public contract/domain type or changes responsibility, dependency direction, lifetime, transaction boundary, or coordinated behavior.
- Route to `ddd-ca-hex-architect` when a responsibility, module/aggregate boundary, dependency direction, domain-language, compatibility, lifetime, or transaction decision is missing or changes.
- A private implementation helper type may remain local only when it keeps the accepted target, radius, behavior, responsibility, dependency direction, lifetime, and transaction boundary unchanged.
- Do not use a file count, a line count, or the mere existence of a new type as the handoff trigger.

## Return

- local change result and files affected
- dependency radius touched and behavior compatibility notes
- narrow validation performed or explicitly skipped
- required handoff or remaining uncertainty

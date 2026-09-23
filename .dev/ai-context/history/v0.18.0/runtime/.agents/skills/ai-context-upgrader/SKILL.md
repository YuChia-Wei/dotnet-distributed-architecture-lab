---
name: ai-context-upgrader
description: Upgrade an initialized target repository between published framework versions using provenance-aware three-way and semantic-customization reconciliation while preserving target-owned truth.
---

# AI Context Upgrader

This is a thin current-runtime wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/ai-context-upgrader/skill.yaml`
- Human Guide: `.dev/guides/ai-collaboration-guides/AI-CONTEXT-UPGRADER-SKILL-GUIDE.md`
- References:
  - `.dev/standards/AI-CONTEXT-VERSION-POLICY.md`
  - `.ai/assets/skills/ai-context-upgrader/references/upgrade-support-policy.md`
  - `.ai/assets/skills/ai-context-upgrader/references/upgrade-playbook.md`
  - `.ai/assets/skills/ai-context-upgrader/references/three-way-merge-boundaries.md`
  - `.ai/assets/skills/ai-context-upgrader/references/provenance-contract.md`
  - `.ai/assets/skills/ai-context-upgrader/references/output-contract.md`
  - `.ai/assets/skills/ai-context-upgrader/references/role-execution-bindings.yaml`
  - `.ai/assets/skills/ai-context-upgrader/references/role-execution-bindings.schema.yaml`
  - `.ai/assets/skills/ai-context-upgrader/references/delegation-run-contract.md`
  - `.ai/assets/skills/ai-context-upgrader/references/delegation-run-contract.schema.yaml`
  - `.ai/assets/skills/ai-context-governance/references/semantic-customization-lifecycle.md`
  - `.ai/assets/skills/ai-context-governance/templates/customizations.schema.yaml`
  - `.ai/assets/skills/ai-context-governance/templates/effective-rule-state.schema.yaml`
  - `.ai/assets/skills/ai-context-governance/templates/effective-rule-state.template.yaml`
  - `.ai/assets/skills/ai-context-governance/templates/effective-rule-packet.schema.yaml`
  - `.ai/assets/skills/ai-context-upgrader/templates/ai-context-source-template.yaml`
  - `.ai/assets/skills/ai-context-upgrader/templates/provenance-template.yaml`
  - `.ai/assets/skills/ai-context-upgrader/templates/customizations-template.yaml`
  - `.ai/assets/skills/ai-context-upgrader/templates/delegation-run-record.template.yaml`
  - `.ai/assets/skills/ai-context-upgrader/templates/upgrade-remediation-packet.schema.yaml`
  - `.ai/assets/skills/ai-context-upgrader/templates/upgrade-remediation-decision.schema.yaml`
  - `.ai/assets/skills/ai-context-upgrader/templates/upgrade-route-matrix.template.yaml`
  - `.ai/assets/skills/ai-context-upgrader/templates/upgrade-route-matrix.schema.yaml`
  - `.ai/assets/skills/ai-context-upgrader/references/multi-hop-upgrade-transaction-contract.md`
  - `.ai/assets/skills/ai-context-upgrader/templates/multi-hop-upgrade-transaction.template.yaml`
  - `.ai/assets/skills/ai-context-upgrader/templates/multi-hop-upgrade-transaction.schema.yaml`
  - `.ai/assets/shared/CLI-EXECUTION-ROUTING-CONTRACT.md`
  - `.ai/assets/shared/cli-execution-routing.schema.yaml`
  - `.ai/assets/shared/ROLE-EXECUTION-CONTRACT.md`
  - `.ai/assets/shared/provider-neutral-capability-registry.yaml`
  - `.ai/assets/shared/provider-projection-registry.yaml`
- `.ai/scripts/validate-ai-context-target.py`
- `.ai/scripts/plan-ai-context-upgrade.py`
- `.ai/assets/skills/ai-context-upgrader/scripts/compare-ai-context-versions.py`

## Wrapper Rules

Use this wrapper only as the current runtime entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/ai-context-upgrader/skill.yaml`.

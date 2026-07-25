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
  - `.ai/assets/skills/ai-context-upgrader/references/upgrade-playbook.md`
  - `.ai/assets/skills/ai-context-upgrader/references/three-way-merge-boundaries.md`
  - `.ai/assets/skills/ai-context-upgrader/references/provenance-contract.md`
  - `.ai/assets/skills/ai-context-upgrader/references/output-contract.md`
  - `.ai/assets/skills/ai-context-governance/references/semantic-customization-lifecycle.md`
  - `.ai/assets/skills/ai-context-governance/templates/customizations.schema.yaml`
  - `.ai/assets/skills/ai-context-upgrader/templates/ai-context-source-template.yaml`
  - `.ai/assets/skills/ai-context-upgrader/templates/provenance-template.yaml`
  - `.ai/assets/skills/ai-context-upgrader/templates/customizations-template.yaml`
  - `.ai/scripts/validate-ai-context-target.py`

## Wrapper Rules

Use this wrapper only as the current runtime entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/ai-context-upgrader/skill.yaml`.

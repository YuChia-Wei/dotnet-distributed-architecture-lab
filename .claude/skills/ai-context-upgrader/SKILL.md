---
name: ai-context-upgrader
description: Upgrade an already initialized target repository between published versions of this AI context framework using provenance-aware three-way comparison while preserving target-owned truth and local overrides.
---

# AI Context Upgrader

This is a thin Claude-compatible wrapper.

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
  - `.ai/assets/skills/ai-context-upgrader/templates/ai-context-source-template.yaml`

## Wrapper Rules

Use this wrapper only as a compatibility entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/ai-context-upgrader/skill.yaml`.

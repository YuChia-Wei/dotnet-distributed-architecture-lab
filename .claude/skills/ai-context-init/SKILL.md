---
name: ai-context-init
description: Initialize a target repository after this AI context framework is copied in by scanning repo facts, refreshing repo-specific context, and atomically creating provenance plus the customization ledger only from credible source evidence.
---

# AI Context Init

This is a thin Claude-compatible wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/ai-context-init/skill.yaml`
- Human Guide: `.dev/guides/ai-collaboration-guides/AI-CONTEXT-INIT-SKILL-GUIDE.md`
- References:
  - `.ai/assets/skills/ai-context-init/references/scan-playbook.md`
  - `.ai/assets/skills/ai-context-init/references/migration-boundaries.md`
  - `.ai/assets/skills/ai-context-init/references/escalation-checklist.md`
  - `.ai/assets/skills/ai-context-init/references/delegation-rules.md`
  - `.ai/assets/skills/ai-context-init/references/document-targets.md`
  - `.ai/assets/skills/ai-context-init/references/output-contract.md`
  - `.ai/assets/skills/ai-context-governance/references/semantic-customization-lifecycle.md`
  - `.ai/assets/skills/ai-context-governance/templates/customizations.schema.yaml`
  - `.ai/assets/skills/ai-context-init/templates/project-config.template.yaml`
  - `.ai/assets/skills/ai-context-init/templates/technology-selection.schema.yaml`
  - `.ai/assets/skills/ai-context-init/templates/public-template-manifest.yaml`
  - `.ai/assets/sub-agent-role-prompts/context-translator/sub-agent.yaml`
  - `.ai/assets/skills/ai-context-upgrader/templates/provenance-template.yaml`
  - `.ai/assets/skills/ai-context-upgrader/templates/customizations-template.yaml`

## Wrapper Rules

Use this wrapper only as a compatibility entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/ai-context-init/skill.yaml`.

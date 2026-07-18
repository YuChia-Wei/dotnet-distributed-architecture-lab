---
name: repo-structure-sync
description: Initialize a target repository after this AI context framework is copied in by scanning repo facts and refreshing repo-specific README, `.dev/`, `.ai/`, and `AGENTS.md` sections without rewriting framework-level collaboration rules.
---

# Repo Structure Sync

This is a thin current-runtime wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/repo-structure-sync/skill.yaml`
- Human Guide: `.dev/guides/ai-collaboration-guides/REPO-STRUCTURE-SYNC-SKILL-GUIDE.md`
- References:
  - `.ai/assets/skills/repo-structure-sync/references/scan-playbook.md`
  - `.ai/assets/skills/repo-structure-sync/references/migration-boundaries.md`
  - `.ai/assets/skills/repo-structure-sync/references/escalation-checklist.md`
  - `.ai/assets/skills/repo-structure-sync/references/delegation-rules.md`
  - `.ai/assets/skills/repo-structure-sync/references/document-targets.md`
  - `.ai/assets/skills/repo-structure-sync/references/output-contract.md`
  - `.ai/assets/skills/repo-structure-sync/templates/project-config.template.yaml`
  - `.ai/assets/skills/repo-structure-sync/templates/public-template-manifest.yaml`
  - `.ai/assets/sub-agent-role-prompts/context-translator/sub-agent.yaml`
  - `.ai/assets/skills/ai-context-upgrader/templates/ai-context-source-template.yaml`

## Wrapper Rules

Use this wrapper only as the current runtime entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/repo-structure-sync/skill.yaml`.

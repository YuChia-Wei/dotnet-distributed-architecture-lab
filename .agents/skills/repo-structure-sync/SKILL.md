---
name: repo-structure-sync
description: Scan a freshly copied target git repository and refresh repo-specific architecture sections in `.dev/`, `.ai/`, and `agents.md`. Use when Codex needs to adapt this template to a new .NET repo by inventorying solution structure, projects, stack facts, and documentation truth without rewriting framework-level collaboration rules.
---

# Repo Structure Sync

This is a thin current-runtime wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/repo-structure-sync/skill.yaml`
- Human Guide: `.dev/guides/ai-collaboration-guides/REPO-STRUCTURE-SYNC-SKILL-GUIDE.md`
- References:
  - `.ai/assets/skills/repo-structure-sync/references/scan-playbook.md`
  - `.ai/assets/skills/repo-structure-sync/references/escalation-checklist.md`
  - `.ai/assets/skills/repo-structure-sync/references/delegation-rules.md`
  - `.ai/assets/skills/repo-structure-sync/references/document-targets.md`
  - `.ai/assets/skills/repo-structure-sync/references/output-contract.md`

## Wrapper Rules

Use this wrapper only as the current runtime entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/repo-structure-sync/skill.yaml`.

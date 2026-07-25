---
name: repo-structure-sync
description: Deprecated compatibility alias for ai-context-init. Use only when an existing request or downstream repository still names repo-structure-sync; route new target-repository initialization work to ai-context-init without rewriting historical provenance.
---

# Repo Structure Sync Compatibility Entry

This identifier is deprecated but has no scheduled removal release.
This identifier is a deprecated compatibility wrapper.

- Registry: `.ai/assets/skills/README.MD`
- Active skill: `ai-context-init`
- Canonical spec: `.ai/assets/skills/ai-context-init/skill.yaml`
- Compatibility contract: `.ai/assets/skills/repo-structure-sync/skill.yaml`
- Human guide: `.dev/guides/ai-collaboration-guides/REPO-STRUCTURE-SYNC-SKILL-GUIDE.md`

Route new work to `ai-context-init`. Preserve historical identifiers in
existing workflows, tasks, assessments, releases, `initialized_by`, and
provenance records.

Use this wrapper only as a deprecated compatibility entry.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/repo-structure-sync/skill.yaml`.

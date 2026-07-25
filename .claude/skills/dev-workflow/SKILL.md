---
name: dev-workflow
description: Deprecated compatibility alias for software-development-orchestrator. Use only when an existing request or downstream repository still names dev-workflow; route new multi-stage software-development orchestration to software-development-orchestrator without rewriting historical workflow ownership.
---

# Dev Workflow Compatibility Entry

This identifier is deprecated but has no scheduled removal release.
This identifier is a deprecated compatibility wrapper.

- Registry: `.ai/assets/skills/README.MD`
- Active skill: `software-development-orchestrator`
- Canonical spec:
  `.ai/assets/skills/software-development-orchestrator/skill.yaml`
- Compatibility contract: `.ai/assets/skills/dev-workflow/skill.yaml`
- Human guide: `.dev/guides/ai-collaboration-guides/DEV-WORKFLOW-SKILL-GUIDE.md`

Route new work to `software-development-orchestrator`. Preserve historical
identifiers in existing workflows, tasks, assessments, releases, and
provenance records.

Use this wrapper only as a deprecated compatibility entry.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/dev-workflow/skill.yaml`.

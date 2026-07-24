---
name: dev-workflow
description: Coordinate multi-stage software and product development lifecycles by deciding direct mode versus workflow mode, creating development artifacts, routing development stages to specialist skills, and managing validation and commit checkpoints.
---

# Dev Workflow

This is a thin Claude-compatible wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/dev-workflow/skill.yaml`
- Human Guide: `.dev/guides/ai-collaboration-guides/DEV-WORKFLOW-SKILL-GUIDE.md`
- References:
  - `.ai/assets/skills/dev-workflow/references/routing-playbook.md`
  - `.ai/assets/skills/dev-workflow/references/skill-discovery-playbook.md`
  - `.ai/assets/skills/dev-workflow/references/capability-profile.md`
  - `.ai/assets/skills/dev-workflow/references/capability-profile.yaml`
  - `.ai/assets/skills/dev-workflow/references/fallback-playbooks.md`
  - `.ai/assets/skills/dev-workflow/references/runtime-coordination.md`
  - `.ai/assets/skills/dev-workflow/references/workflow-artifact-playbook.md`
  - `.ai/assets/skills/dev-workflow/references/output-contract.md`
- Templates:
  - `.ai/assets/skills/dev-workflow/templates/workflow-locator-template.yaml`
  - `.ai/assets/skills/dev-workflow/templates/development-workflow-plan-template.md`
  - `.ai/assets/skills/dev-workflow/templates/development-workflow-task-template.json`
  - `.ai/assets/skills/dev-workflow/templates/development-review-report-template.md`

## Wrapper Rules

Use this wrapper only as a compatibility entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/dev-workflow/skill.yaml`.

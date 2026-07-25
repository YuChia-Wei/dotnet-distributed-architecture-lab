---
name: software-development-orchestrator
description: Coordinate high-level multi-stage software and product development intent without requiring skill names by deciding direct versus workflow mode, routing capabilities, honoring approval pauses, and managing target-aware tests, validation, and durable commit checkpoints.
---

# Software Development Orchestrator

This is a thin current-runtime wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/software-development-orchestrator/skill.yaml`
- Handoff Policy: `.dev/standards/WORKFLOW-HANDOFF-POLICY.md`
- Human Guide: `.dev/guides/ai-collaboration-guides/SOFTWARE-DEVELOPMENT-ORCHESTRATOR-SKILL-GUIDE.md`
- References:
  - `.ai/assets/skills/software-development-orchestrator/references/routing-playbook.md`
  - `.ai/assets/skills/software-development-orchestrator/references/skill-discovery-playbook.md`
  - `.ai/assets/skills/software-development-orchestrator/references/capability-profile.md`
  - `.ai/assets/skills/software-development-orchestrator/references/capability-profile.yaml`
  - `.ai/assets/skills/software-development-orchestrator/references/fallback-playbooks.md`
  - `.ai/assets/skills/software-development-orchestrator/references/runtime-coordination.md`
  - `.ai/assets/skills/software-development-orchestrator/references/workflow-artifact-playbook.md`
  - `.ai/assets/skills/software-development-orchestrator/references/output-contract.md`
  - `.ai/assets/skills/software-development-orchestrator/references/acceptance-oracle.md`
- Templates:
  - `.ai/assets/skills/software-development-orchestrator/templates/workflow-locator-template.yaml`
  - `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
  - `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-task-template.json`
  - `.ai/assets/skills/software-development-orchestrator/templates/development-review-report-template.md`

## Wrapper Rules

Use this wrapper only as the current runtime entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/software-development-orchestrator/skill.yaml`.

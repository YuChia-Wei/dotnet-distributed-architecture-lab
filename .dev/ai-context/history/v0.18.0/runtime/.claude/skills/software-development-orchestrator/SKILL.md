---
name: software-development-orchestrator
description: Coordinate high-level multi-stage software and product development intent without requiring skill names by deciding direct versus workflow mode, routing capabilities, honoring approval pauses, and managing target-aware tests, validation, and durable commit checkpoints.
---

# Software Development Orchestrator

This is a thin Claude-compatible wrapper.

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
  - `.ai/assets/skills/software-development-orchestrator/references/role-execution-playbook.md`
  - `.ai/assets/skills/software-development-orchestrator/references/workflow-artifact-playbook.md`
  - `.ai/assets/skills/software-development-orchestrator/references/output-contract.md`
  - `.ai/assets/skills/software-development-orchestrator/references/validation-activation-policy.md`
  - `.ai/assets/skills/software-development-orchestrator/references/acceptance-oracle.md`
  - `.ai/assets/skills/software-development-orchestrator/templates/external-task-delegation.schema.yaml`
  - `.ai/assets/skills/software-development-orchestrator/templates/external-task-dispatch.template.yaml`
  - `.ai/assets/skills/software-development-orchestrator/templates/external-task-completion.template.yaml`
  - `.ai/assets/skills/software-development-orchestrator/scripts/validate-external-task-delegation.py`
  - `.ai/assets/shared/ROLE-EXECUTION-CONTRACT.md`
  - `.ai/assets/shared/AGENT-EXECUTION-GUARDRAILS-CONTRACT.md`
  - `.ai/assets/shared/agent-execution-guardrails.schema.yaml`
  - `.ai/scripts/validate-agent-execution-guardrails.py`
- Templates:
  - `.ai/assets/skills/software-development-orchestrator/templates/workflow-locator-template.yaml`
  - `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
  - `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-task-template.json`
  - `.ai/assets/skills/software-development-orchestrator/templates/development-review-report-template.md`

## Wrapper Rules

Use this wrapper only as a compatibility entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/software-development-orchestrator/skill.yaml`.

---
name: ai-context-governance
description: Govern AI collaboration context boundaries, documentation quality, skill routing, runtime wrapper sync, migrations, and the audit-to-remediation lifecycle. Use when Claude needs to organize `.ai`, `.dev`, `.agents`, or `.claude`, remediate AI context audit findings, coordinate a post-remediation audit, close an AI context maintenance workflow, or keep this work out of product-development skills.
---

# AI Context Governance

This is a thin Claude-compatible wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/ai-context-governance/skill.yaml`
- Human Guide: `.dev/guides/ai-collaboration-guides/AI-CONTEXT-GOVERNANCE-SKILL-GUIDE.md`
- References:
  - `.ai/assets/skills/ai-context-governance/references/context-boundary-playbook.md`
  - `.ai/assets/skills/ai-context-governance/references/language-policy-playbook.md`
  - `.ai/assets/skills/ai-context-governance/references/workflow-and-commit-playbook.md`
  - `.ai/assets/skills/ai-context-governance/references/output-contract.md`
  - `.ai/assets/skills/ai-context-governance/references/audit-remediation-lifecycle.md`
- Templates:
  - `.ai/assets/skills/ai-context-governance/templates/workflow-locator-template.yaml`
  - `.ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md`
  - `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-task-template.json`
  - `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`

## Wrapper Rules

Use this wrapper only as a compatibility entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/ai-context-governance/skill.yaml`.

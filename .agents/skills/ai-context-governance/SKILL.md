---
name: ai-context-governance
description: Govern AI collaboration context boundaries, documentation quality, skill routing, runtime wrapper sync, migrations, and assessment-to-remediation lifecycles. Use when Codex needs to organize `.ai`, `.dev`, `.agents`, or `.claude`, intake assessment findings, coordinate remediation and verification assessments, close an AI context maintenance workflow, or keep this work out of product-development skills.
---

# AI Context Governance

This is a thin current-runtime wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Assessment Policy: `.dev/standards/ASSESSMENT-ARTIFACT-POLICY.md`
- Handoff Policy: `.dev/standards/WORKFLOW-HANDOFF-POLICY.md`
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
  - `.ai/assets/skills/ai-context-governance/templates/workflow-handoff-checkpoint-template.yaml`
  - `.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`

## Wrapper Rules

Use this wrapper only as the current runtime entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/ai-context-governance/skill.yaml`.

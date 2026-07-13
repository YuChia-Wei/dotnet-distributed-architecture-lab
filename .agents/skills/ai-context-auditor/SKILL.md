---
name: ai-context-auditor
description: Analyze repository AI context structure, governance, routing, wrappers, indexes, prompts, workflow records, and validation surfaces. Return transient read-only findings in conversation unless the user requests a persisted report; durable audits use owned workflow artifacts. Exclude product source and test code by default; redirect source-code review requests to the repository code-review skill.
---

# AI Context Auditor

This is a thin current-runtime wrapper.

## Canonical Source

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/ai-context-auditor/skill.yaml`
- Human Guide: `.dev/guides/ai-collaboration-guides/AI-CONTEXT-AUDITOR-SKILL-GUIDE.md`
- References:
  - `.ai/assets/skills/ai-context-auditor/references/scope-and-routing.md`
  - `.ai/assets/skills/ai-context-auditor/references/audit-playbook.md`
  - `.ai/assets/skills/ai-context-auditor/references/output-contract.md`
- Report Template: `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-report-template.md`
- Workflow Templates:
  - `.ai/assets/skills/ai-context-auditor/templates/workflow-locator-template.yaml`
  - `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-workflow-plan-template.md`
  - `.ai/assets/skills/ai-context-auditor/templates/ai-context-audit-task-template.json`

## Wrapper Rules

Use this wrapper only as the current runtime entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/ai-context-auditor/skill.yaml`.
Remain read-only with respect to audited context. Hand remediation and lifecycle closure to `ai-context-governance`.

---
name: diagnostic-analyst
description: Diagnose observed failures or performance symptoms through falsification, minimal reproduction and causal isolation; hand off repair without granting implementation authority.
---

# Diagnostic Analyst

This is a thin current-runtime wrapper.

- Registry: `.ai/assets/skills/README.MD`
- Spec: `.ai/assets/skills/diagnostic-analyst/skill.yaml`
- Diagnostic contract: `.ai/assets/skills/diagnostic-analyst/references/diagnostic-contract.md`
- Output contract: `.ai/assets/skills/diagnostic-analyst/references/output-contract.md`
- Human guide: `.dev/guides/ai-collaboration-guides/DIAGNOSTIC-ANALYST-SKILL-GUIDE.md`

- Validator: `.ai/assets/skills/diagnostic-analyst/scripts/validate-diagnostic-record.py`

Use this wrapper only as the current runtime entry.
Keep runtime-specific metadata in this wrapper directory only when the runtime requires it.
If wrapper text and canonical spec differ, follow `.ai/assets/skills/diagnostic-analyst/skill.yaml`.

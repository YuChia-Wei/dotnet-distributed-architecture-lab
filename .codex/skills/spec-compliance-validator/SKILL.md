---
name: spec-compliance-validator
description: Validate .NET code and tests against problem frame specs with a 100 percent gate. Supports CommandedBehaviorFrame and SimpleWorkpieceFrame workflows.
---

# Spec Compliance Validator

Use this as the Codex runtime skill wrapper for problem-frame spec compliance validation.

## Canonical Source

- `.ai/assets/skills/spec-compliance-validator/skill.yaml`

## Quick Start

1. Read `.ai/assets/skills/spec-compliance-validator/references/spec-compliance-rules.md`.
2. Read `.ai/assets/skills/spec-compliance-validator/references/test-validation-steps.md`.
3. Read `.ai/assets/skills/spec-compliance-validator/references/validation-command-templates.md`.
4. Read the target problem frame path and detect the frame type before validating.

## Wrapper Rules

- Treat this file as a thin runtime wrapper only.
- Use `.ai/assets/skills/spec-compliance-validator/skill.yaml` as the canonical source of truth.
- Do not relax the 100 percent compliance gate.



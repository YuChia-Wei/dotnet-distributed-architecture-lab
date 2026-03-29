---
name: ddd-ca-hex-architect
description: Design and refactor architecture in this repository using DDD, Clean Architecture, CQRS, MQ-first integration, and a Hexagonal Architecture view of ports and adapters. Use when Codex should directly execute this repository's architecture workflow as a runtime skill.
---

# DDD CA HEX Architect

Use this as the Codex runtime skill wrapper for the repository's DDD + Clean Architecture + Hexagonal Architecture workflow.

## Canonical Source

- `.ai/assets/skills/ddd-ca-hex-architect/skill.yaml`

## Human-Facing Guide

- `.dev/guides/ai-collaboration-guides/DDD-CA-HEX-ARCHITECT-SKILL-GUIDE.md`

## Quick Start

1. Read `.dev/ARCHITECTURE.MD` and `.dev/requirement/TECH-STACK-REQUIREMENTS.MD`.
2. Read [references/source-map.md](references/source-map.md) to choose the relevant design slice.
3. Read [references/architecture-playbook.md](references/architecture-playbook.md) before proposing architecture changes.
4. Read [references/design-deliverables.md](references/design-deliverables.md) when the user wants an architecture artifact, staged refactor plan, or prompt/workflow redesign.

## Wrapper Rules

- Treat this file as a thin runtime wrapper only.
- Use `.ai/assets/skills/ddd-ca-hex-architect/skill.yaml` as the canonical source of truth.
- Prefer canonical references over duplicating detailed guidance here.
- If this runtime wrapper and the canonical source diverge, follow the canonical source and surface the mismatch.

## Default Output

1. Context and goal
2. Architecture decisions
3. Layer, port, and adapter placement
4. Contract, event, and persistence impact
5. Files, prompts, and ADRs to update
6. Risks and tradeoffs

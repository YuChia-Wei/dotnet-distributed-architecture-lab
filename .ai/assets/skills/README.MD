# Skill Specs

This directory contains runtime-neutral canonical skill specs.

## Purpose

Use `.ai/assets/skills/` as the source of truth for top-level skills. Runtime wrappers under `.agents/skills/` and `.claude/skills/` should stay thin and point back to these canonical specs.

## Usage

Each skill should keep its canonical entry in `skill.yaml`, with optional `references/`, `prompts/`, and `examples/` when needed.

The canonical skill registry currently includes:

- `ai-context-governance`
- `ai-context-auditor`
- `bdd-gwt-test-designer`
- `code-reviewer`
- `dev-workflow`
- `ddd-ca-hex-architect`
- `local-change-implementer`
- `problem-frame-author`
- `repo-structure-sync`
- `requirement-author`
- `slice-implementer`
- `spec-author`
- `spec-compliance-validator`

## Boundary

Do not put runtime-specific metadata, full wrapper instructions, or human-facing tutorial content here. Put runtime wrappers under their runtime directories and human-facing guides under `.dev/guides/`.

# Skill Specs

This directory contains runtime-neutral canonical skill specs.

## Purpose

Use `.ai/assets/skills/` as the source of truth for top-level skills. Runtime wrappers under `.agents/skills/` and `.claude/skills/` should stay thin and point back to these canonical specs.

## Usage

Each skill should keep its canonical entry in `skill.yaml`, with optional
`references/`, `prompts/`, `examples/`, and `scripts/` when needed. Put an
executable or contract test under `scripts/` only when exactly one canonical
skill owns its behavior. Keep multi-skill, provider, release, package, workflow,
and source-repository-wide automation under `.ai/scripts/`; retain published
legacy command paths only as explicit thin compatibility entrypoints.

The canonical skill registry currently includes:

- `ai-context-governance`
- `ai-context-release-closeout` (source-repository-only historical/exception recovery; never packaged)
- `ai-context-auditor`
- `ai-context-init`
- `ai-context-upgrader`
- `bdd-gwt-test-designer`
- `code-reviewer` (`dotnet-backend` selected; unavailable in the core-only view)
- `diagnostic-analyst`
- `ddd-ca-hex-architect`
- `local-change-implementer`
- `problem-frame-author`
- `requirement-author`
- `slice-implementer`
- `software-development-orchestrator`
- `spec-author`
- `spec-compliance-validator`

## Retired Identifiers

[`transitions/v0.16.0.yaml`](transitions/v0.16.0.yaml) retires
`repo-structure-sync` (replacement: `ai-context-init`) and `dev-workflow`
(replacement: `software-development-orchestrator`) in v0.16.0. Their canonical
specs and runtime wrappers are absent. On a new request using either retired
identifier, explicitly report: "Skill '<identifier>' was retired in v0.16.0.
Use '<replacement>' for a new request." Do not silently dispatch an alias.

The portable deterministic request check is
`python .ai/scripts/skill_identifier_lifecycle.py <identifier>`; a retired or
unknown runtime request returns a nonzero status. `--context historical` accepts
a known retired identifier only as evidence and preserves its original value.
This is an explicit input-context boundary, not automatic history detection.

[`transitions/v0.6.0.yaml`](transitions/v0.6.0.yaml) remains the immutable record
of the earlier activation and its then-unscheduled removal. Do not rewrite
historical workflow, task, assessment, release, provenance, commit, or evaluation
identifiers. Continued execution uses the active replacement without rewriting
past evidence. New runtime availability is governed by the retirement manifest.

Downstream upgrade packages use the previous release's verified file inventory:
remove unchanged framework-owned entries; retain modified or target-owned
entries for explicit owner reconciliation. Missing baseline evidence blocks
removal. The v0.6.0/v0.9.0 fixture coverage does not authorize a direct upgrade
edge or publication; the selected release must still supply its verified route.

## Boundary

Do not put runtime-specific metadata, full wrapper instructions, or human-facing tutorial content here. Put runtime wrappers under their runtime directories and human-facing guides under `.dev/guides/`.

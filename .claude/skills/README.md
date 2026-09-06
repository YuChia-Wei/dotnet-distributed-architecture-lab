# Claude Skill Wrappers

This directory contains Claude-compatible skill wrappers.

## Role

- `.claude/skills/`
  - Claude-compatible wrapper root
- `.ai/assets/skills/`
  - canonical skill registry and source of truth
- `.dev/guides/ai-collaboration-guides/`
  - human-facing guides

## Usage

1. Start with `.ai/assets/skills/README.MD` for the complete canonical skill registry.
2. Read the matching `skill.yaml` for purpose, inputs, outputs, constraints, wrapper targets, and human guide.
3. Use `.claude/skills/<skill>/SKILL.md` only when a Claude-compatible wrapper is needed.

## Available Wrappers

- `ai-context-governance`
- `ai-context-release-closeout` (source-repository-only historical/exception recovery)
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

`repo-structure-sync` and `dev-workflow` are retired in v0.16.0 and have no runtime wrappers. For a new request, report the retired identifier and its replacement (`ai-context-init` and `software-development-orchestrator`, respectively); do not silently route it. Preserve historical identifiers. The canonical registry owns the tombstone and deterministic diagnostic.

## Wrapper Rules

- A wrapper must not become the source of truth for skill rules.
- Add or update the canonical spec before adding or updating a wrapper.
- If the canonical spec and wrapper conflict, follow `.ai/assets/skills/`.
- Each wrapper `SKILL.md` should only keep canonical spec links, human guide links, reference links, and runtime-specific metadata.

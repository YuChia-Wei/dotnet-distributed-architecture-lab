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
- `ddd-ca-hex-architect`
- `local-change-implementer`
- `problem-frame-author`
- `requirement-author`
- `slice-implementer`
- `software-development-orchestrator`
- `spec-author`
- `spec-compliance-validator`

## Deprecated Compatibility Entries

[`transitions/v0.6.0.yaml`](transitions/v0.6.0.yaml) records the approved
`repo-structure-sync` to `ai-context-init` and `dev-workflow` to
`software-development-orchestrator` mappings. Both target identifiers are
active. The historical identifiers remain thin deprecated compatibility
entries with no scheduled removal release; do not rewrite historical workflow,
task, assessment, release, or provenance values.

## Boundary

Do not put runtime-specific metadata, full wrapper instructions, or human-facing tutorial content here. Put runtime wrappers under their runtime directories and human-facing guides under `.dev/guides/`.

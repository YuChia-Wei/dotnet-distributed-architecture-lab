# Context Boundary Playbook

Use this playbook when classifying, moving, or cleaning AI collaboration context.

## Evidence Order

1. User request and active workflow task
2. `.dev/standards/AI-CONTEXT-BOUNDARY.md`
3. Existing folder placement
4. Canonical registries and wrapper indexes
5. File content

## Classification Columns

Use these columns for inventories:

| Column | Values |
| --- | --- |
| Audience | `agent`, `human`, `both` |
| Scope | `universal`, `dotnet-backend`, `repo-specific`, `runtime-wrapper` |
| Language | `en`, `zh-TW`, `bilingual-entry` |
| Action | `keep`, `split`, `move`, `rewrite`, `index-sync`, `defer` |

## Placement Rules

- Universal agent context belongs under `.ai/assets/shared/`.
- .NET backend-only context belongs under `.ai/assets/tech-stacks/dotnet-backend/`.
- Canonical skill specs belong under `.ai/assets/skills/<skill-id>/`.
- Runtime wrappers belong under `.agents/skills/<skill-id>/` and `.claude/skills/<skill-id>/`.
- Human-facing guides belong under `.dev/guides/`.
- Project truth belongs under `.dev/`.

## Metadata Rule

Use metadata for machine-readable canonical assets only. Do not add metadata to every Markdown file to compensate for unclear folder placement.

## Out-of-Scope Signals

Escalate or defer when cleanup touches:

- frontend or full-stack template design;
- production architecture redesign;
- BDD scenario design;
- code implementation;
- broad translation migration.

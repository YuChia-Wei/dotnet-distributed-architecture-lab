# Prompt Portability Rules

Use these rules when creating or updating files in `.ai/prompts/` so prompts remain reusable across repositories.

## Mandatory Rules
- Do not reference repository-specific ADR numbers (for example: `ADR-0xx`).
- Do not reference repository-specific domain terms, route names, aggregate names, or folder names.
- Do not hardcode project names, solution names, or bounded-context names.
- Use neutral placeholders (`Entity`, `WorkItem`, `Container`, `DomainObject`) in examples.
- Keep project-specific decisions as "Project Decision Slot" notes, not fixed policy text.

## Allowed References
- Shared standards that are intentionally copied with `.ai` and `.dev` (for example: `project-config.yaml`).
- Generic architecture patterns (DDD, CQRS, Outbox, Event Sourcing).
- Technology constraints explicitly declared by the target framework profile.

## ADR Usage Rule
- If a prompt needs a decision reference, use neutral labels:
- `Project Decision Slot: Serialization baseline`
- `Project Decision Slot: Environment profile matrix`
- Never hardcode a numeric ADR id in prompt text.

## Example Conversion
- Before: `RTK Query Cache Rules (ADR-XXX)`
- After: `RTK Query Cache Rules (Project Decision Slot: Cache Invalidation Policy)`

## Pre-Commit Checklist
- `rg -n "ADR-[0-9]{3}" .ai/prompts` returns no results.
- `rg -n "ProjectNameA|ProjectNameB|DomainTermA|DomainTermB" .ai/prompts` returns no results.
- Example code uses neutral names and can be copied without domain rewrite.

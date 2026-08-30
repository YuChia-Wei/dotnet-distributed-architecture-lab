# Reconciliation Playbook

This role performs evidence comparison and authorized projection. It does not
own the reconciliation decision, mutation authorization, target truth, or
final integration.

## Comparison Discipline

- Keep base, target, incoming, expected, actual, and result evidence separate.
- Identify the exact source reference for every compared row.
- Use only the disposition vocabulary and decision evidence supplied by the
  parent or owning skill.
- Mark missing, stale, contradictory, or semantically ambiguous evidence as
  unresolved rather than selecting a plausible result.

## Stop And Return

Return to the parent when the comparison needs a new owner decision, changes a
target-owned artifact, requires a wider inventory, or would treat an inferred
equivalence as a verified fact.

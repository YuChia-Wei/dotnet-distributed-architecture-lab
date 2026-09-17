# Architecture Playbook

## Method And Authority

Use DDD to examine language, responsibility and invariant ownership, Clean
Architecture to examine dependency direction, and Hexagonal Architecture to
separate application ports from external adapters. Preserve this skill's
method purpose without treating every method pattern as mandatory structure.
Confirm the target's adopted boundaries and quality constraints first.
CQRS, event sourcing, broker selection and physical project splitting need
applicable target decisions; do not invent adoption.

Read the shared artifact design/review contract and select `design` or `review`.
Use `source-map.md` for applicable technology guidance. A profile's conventions
must not leak into an unselected target. Conflicting authority stops the
affected decision; current code describes behavior but does not override an
accepted requirement merely by existing.

## Design Sequence

1. Identify the business capability, requirement/AC IDs, workload and quality
   constraints. Label missing inputs and provisional assumptions.
2. Define responsibility, language, data ownership and consistency boundaries.
   Explain each aggregate or module and its invariant; avoid speculative splits.
3. Place inbound/outbound ports and adapters. Keep business decisions independent
   of transport, persistence, dependency injection and vendor APIs.
4. Connect commands, queries and reactions only where the requested model needs
   them. State the result, error, transaction and external-effect contracts.
5. Compare credible alternatives and costs. Explain failure windows, recovery,
   observability and ownership for relevant dependencies and side effects.
6. Describe compatibility, migration and rollout for existing consumers when
   relevant, plus observable acceptance and the evidence needed to validate it.

## Boundary Questions

- Does each context/module have a clear owner and vocabulary?
- Which invariant requires atomicity, and what intermediate state is acceptable?
- Does a proposed transaction cross an ownership boundary? Do coordination or
  compensation satisfy the requirement? Record unresolved decisions explicitly.
- Does each dependency need a port, and can failure/time/data be controlled for
  meaningful testing? Do not create abstractions without an observable purpose.
- Which data and contract changes affect existing users or operational recovery?

For an adopted .NET profile, retain its stricter transaction, repository, MQ,
DI and testing rules through the selected supplement. This method playbook
neither duplicates nor weakens those applicable rules.

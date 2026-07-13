# Domain Rules (Dotnet)

Use this file for reusable domain modeling constraints across repositories.
Keep rules generic and avoid product-specific terminology.

## Aggregate Invariant Rules
- Enforce invariants inside aggregate behavior methods, not controllers or DTO mappers.
- Validate invariants before emitting events.
- If temporary inconsistency is required during a transaction, document it explicitly and resolve within the same command flow.

## Domain Event Design Rules
- Prefer one canonical event per behavior with clear before/after fields when needed.
- Use past-tense event names (`EntityCreated`, `StatusChanged`, `ItemRemoved`).
- Include metadata for traceability (actor, timestamp, correlation/causation identifiers where available).
- Keep event payloads stable and serialization-friendly.

## State Transition Rules
- Model allowed transitions explicitly (state machine, guard clauses, or policies).
- Reject invalid transitions with domain-level exceptions.
- Keep transition side effects deterministic and testable.

## Value Object Rules
- Use immutable value objects.
- Validate invariants at construction time.
- Keep equality semantics value-based only.

## Multi-Role / Combination Rules
- For mutually exclusive combinations, centralize validation in one domain policy/helper.
- Do not duplicate combination rules across API/application layers.

## Integration Safety Rules
- Domain model must not depend on transport contracts.
- Cross-context communication contracts belong to boundary/application layers.

## TODO Guidance
- If project-specific details are unknown, keep concise TODOs and tag them with owning layer (`Domain`, `Application`, `Infrastructure`).

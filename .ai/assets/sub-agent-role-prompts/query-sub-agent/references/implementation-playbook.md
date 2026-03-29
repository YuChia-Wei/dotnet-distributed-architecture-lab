# Query Sub-Agent Implementation Playbook

Use this delegated sub-agent role when the main agent needs a worker focused on query-side use case implementation.

## Mandatory References

- `.ai/assets/shared/common-rules.md`
- `.ai/assets/shared/domain-rules.md`

## Rules

- Queries must not modify domain state
- Use read models or projections for query paths
- Return DTOs, never domain entities
- Use WolverineFx query handlers
- Keep endpoint and DTO naming aligned with current bounded context terminology

## Query-Side Storage Pattern

- Use Archive for read-model CRUD on the query side
- Repositories are for the write model only
- Archive interfaces must not add custom methods

Naming:

- Interface: `XxxArchive`
- Implementation: `EfCoreXxxArchive` or `InMemoryXxxArchive`

## Optional Filter Sentinel

- If the API uses a sentinel value for "unassigned" or "all", keep mapping centralized in query handlers
- Normalize sentinel values before querying

## Client Navigation Support

- Query endpoints should include state fields required by client routing decisions
- Keep routing decisions in the client layer; server should provide canonical state only

## Output Structure

- `src/Application/<Aggregate>/UseCases/Queries/`


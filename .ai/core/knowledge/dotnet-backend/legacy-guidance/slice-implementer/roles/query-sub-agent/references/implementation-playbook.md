# Query Sub-Agent Implementation Playbook

Reference-only technical guidance. Apply the target-selected architecture and technology;
this projection neither activates a runtime role nor creates an additional normative owner.

Technical reference for query-side use case implementation. Loading this material does not dispatch a worker.

## Mandatory References

- `../../../../../shared/common-rules.md`
- `../../../../../shared/domain-rules.md`

## Rules

- Queries must not modify domain state
- Use read models or projections for query paths
- Return DTOs, never domain entities
- Implement `I<Operation>UseCase` and `<Operation>UseCase` with `ExecuteAsync` and
  a non-optional `CancellationToken`.
- Use a transport-neutral Use Case input/output contract.
- Add a query Handler only for a real dispatch entry; keep Wolverine conditional.
- A Controller uses the query Use Case by default. Direct Query Repository/Service
  access is allowed only for an explicitly selected pure-query endpoint.
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

- `src/Application/UseCases/<Operation>/`

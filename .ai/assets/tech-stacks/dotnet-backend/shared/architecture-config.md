# Architecture Config (Dotnet)

## Source of Truth
- A generated `.dev/project-config.yaml` may summarize confirmed architecture mode, database libraries, and profile support in a target repository.
- Repository code, project files, and package references remain stronger evidence.

## Supported Patterns
- **inmemory**: In-memory repository + message broker
- **outbox**: Transactional message store using the target repository's selected adapter
- **eventsourcing**: Event store + replay

## Mapping Rules
- Command flows use an explicit Use Case and
  `IAggregateRepository<TAggregate, TId>` for Aggregate Roots
- Query flows default to an explicit Use Case and read-only ports inheriting
  `IQueryRepository`
- Reactor handlers process event data (not domain entities)
- Dispatch/message Handlers map delivery input and invoke one Use Case; they do
  not own orchestration
- Use Cases depend on project-owned outbound event publisher ports; Wolverine
  belongs to Infrastructure/adapter code
- Persistence libraries and databases are selected by the target repository

## DI Registration Rules
- Register repositories per profile/environment
- Prefer explicit registration over scanning

## Outbox Pattern (when WolverineFx is selected)
- Persist event first
- Relay to message broker
- Keep metadata for audit

# Architecture Config (Dotnet)

## Source of Truth
- `project-config.yaml` drives architecture mode, database settings, and profile support

## Supported Patterns
- **inmemory**: In-memory repository + message broker
- **outbox**: EF Core + Outbox message store
- **eventsourcing**: Event store + replay

## Mapping Rules
- Command handlers use write model repositories
- Query handlers use read model projections
- Reactor handlers process event data (not domain entities)

## DI Registration Rules
- Register repositories per profile/environment
- Prefer explicit registration over scanning

## Outbox Pattern (WolverineFx)
- Persist event first
- Relay to message broker
- Keep metadata for audit

# .NET Code Review Checklist

This checklist enforces DDD, Clean Architecture, CQRS, Event Sourcing, Outbox, and Testing rules for .NET.

## Global Must-Fail Conditions
- Profile/environment hardcoded in tests
- BaseTestClass usage in tests
- Controllers contain business logic
- DTOs defined as inner classes
- Public generic writable CRUD repositories
- Aggregate repositories that expose query or bulk convenience methods
- Direct state assignment in aggregate constructors

## Aggregate Root (Event Sourcing)
- [ ] Aggregate state changes only via Apply/When
- [ ] Events are immutable and include metadata
- [ ] No direct state assignment in constructors
- [ ] Postconditions in domain methods (ensure)

## Domain Events
- [ ] Event types are immutable records
- [ ] Metadata includes audit fields
- [ ] Event mapping registered for serialization

## Entities / Value Objects
- [ ] Use Objects/Guard for null checks
- [ ] No Contract usage in VO/Entity/Event
- [ ] Value Objects are immutable

## Use Case / Application
- [ ] Command/Query separation
- [ ] Command handlers use write models only
- [ ] Query handlers do not mutate state
- [ ] Result/ExitCode handling is explicit
- [ ] Explicit Unit of Work appears only for documented exceptional strong consistency

## Repository
- [ ] Aggregate writes use `IAggregateRepository<TAggregate, TId>` or its
      `IDomainRepository<TAggregate, TId>` compatibility alias
- [ ] Repository generic type is an Aggregate Root
- [ ] Base aggregate contract exposes only `FindByIdAsync` and `SaveAsync`
- [ ] Read ports inherit `IQueryRepository` and expose no write capability
- [ ] Batch ports, when target-specific, document measured need and complete
      execution semantics

## Outbox
- [ ] Events persisted before publishing
- [ ] Outbox schema includes metadata
- [ ] Configuration registered via DI

## Controller
- [ ] Thin controllers; DTO mapping only
- [ ] Proper HTTP status codes
- [ ] DTOs are separate files
- [ ] Validation attributes applied

## Testing
- [ ] xUnit tests use Given-When-Then structure and naming; BDDfy is the default unless the target team explicitly opted out, and 3A is not used as a substitute
- [ ] `.feature` files are treated as optional and are only required when supplied/requested or selected by the target profile
- [ ] No BaseTestClass
- [ ] NSubstitute used for mocks
- [ ] Async-safe event verification

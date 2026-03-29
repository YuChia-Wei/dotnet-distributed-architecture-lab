# .NET Code Review Checklist

This checklist enforces DDD, Clean Architecture, CQRS, Event Sourcing, Outbox, and Testing rules for .NET.

## Global Must-Fail Conditions
- Profile/environment hardcoded in tests
- BaseTestClass usage in tests
- Controllers contain business logic
- DTOs defined as inner classes
- Custom repository interfaces for domain writes
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
- [ ] xUnit + BDDfy with Gherkin-style naming (no `.feature` files)
- [ ] No BaseTestClass
- [ ] NSubstitute used for mocks
- [ ] Async-safe event verification

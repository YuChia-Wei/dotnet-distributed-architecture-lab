# .NET Coding Standards

This directory contains all .NET coding-standard documents. Each document focuses on standards and best practices for a specific area.

---

## 📚 Standards Document Index

### Core Domain Standards
- **[aggregate-standards.md](./aggregate-standards.md)** - Aggregate, Entity, Value Object, and Domain Event rules
  - Aggregate Root design principles
  - Domain Event structure and handling
  - Value Object immutability design
  - Soft Delete implementation requirements
  - 📋 Includes complete code templates

- **[repository-standards.md](./repository-standards.md)** - Repository pattern rules
  - Aggregate Repository and compatibility contract
  - Query Repository marker
  - Physical purge and optional batch capability
  - Transaction / Domain Event lifecycle
  - Conditional adapter guidance

- **[usecase-standards.md](./usecase-standards.md)** - Handler/Use Case layer rules
  - Command vs Query separation principle (CQRS)
  - WolverineFx Handler design
  - Result Pattern error handling
  - 📋 Includes complete Command/Query templates

- **[reactor-standards.md](./reactor-standards.md)** - Reactor/event-handling rules
  - `IReactor<DomainEventData>` interface rules
  - event-to-action flow boundaries
  - replay and duplicate-delivery considerations

### Data Access Standards
- **[projection-standards.md](./projection-standards.md)** - Projection/Query Service pattern rules
  - Read Model design principles
  - EF Core Query implementation
  - Pagination and complex-query handling

- **[archive-standards.md](./archive-standards.md)** - Archive pattern rules
  - Query Model CRUD operations
  - Cross-Bounded-Context reference data
  - Event-driven writes

- **[mapper-standards.md](./mapper-standards.md)** - Mapper design rules
  - Domain and Data object conversion
  - System.Text.Json serialization
  - Static-method design principles

### API and Controller-Layer Standards
- **[controller-standards.md](./controller-standards.md)** - ASP.NET Core Controller rules
  - HTTP status-code usage
  - ProblemDetails error responses
  - Request validation
  - Minimal API vs Controller

### Testing Standards
- **[test-standards.md](./test-standards.md)** - Test coding rules
  - xUnit + BDDfy is the default testing framework; GWT is the minimum requirement and must not be replaced by 3A
  - NSubstitute Mocking (Moq is prohibited)
  - Contract Tests (DBC Precondition validation)
  - WebApplicationFactory integration tests
  - 📋 Includes test templates

- **[profile-configuration-standards.md](./profile-configuration-standards.md)** - Profile/Environment rules
  - `DOTNET_ENVIRONMENT` / `ASPNETCORE_ENVIRONMENT` loading rules
  - `appsettings.{Environment}.json` naming and responsibilities
  - InMemory/Outbox profile-specific DI constraints

---

## 🔴 Key Principle Summary

### Mandatory Core Rules

#### 1. Repository Rules
- ✅ New code uses `IAggregateRepository<Aggregate, AggregateId>`
- ✅ Existing `IDomainRepository<Aggregate, AggregateId>` remains a compatibility contract
- ✅ The shared Aggregate Repository exposes only `FindByIdAsync()` and `SaveAsync()`
- ❌ Child Entity repositories and public generic CRUD repositories are prohibited
- ✅ Query ports implement `IQueryRepository` and remain read-only
- ✅ Physical purge and target-specific batch persistence use separate capabilities

#### 2. Aggregate Design
- ✅ Every Aggregate must support soft deletion (`IsDeleted`)
- ✅ Use public constructors rather than static factory methods
- ✅ Command methods must include `Contract.Ensure` postcondition checks

#### 3. Handler Design (CQRS)
- ✅ Commands and Queries must be separated
- ✅ Define Commands/Queries with `sealed record`
- ✅ Use Constructor Injection; `[FromServices]` is prohibited
- ✅ Use cases, services, mappers, and projections must be registered explicitly through `IServiceCollection`; attribute-based auto registration is prohibited
- ✅ Return `Result<T>` for error handling

#### 4. Testing Requirements
- ✅ Use xUnit + BDDfy by default; when the target team disables BDDfy, C# tests must still use GWT style
- ✅ Use NSubstitute (Moq is prohibited)
- ✅ Do not inherit from BaseTestClass
- ✅ Use `Guid.NewGuid().ToString()` for Aggregate Root IDs
- ✅ See [profile-configuration-standards.md](./profile-configuration-standards.md) for profile and environment rules

---

## 📋 Quick Navigation

### When you need to...
- **Create a new Aggregate** → See [aggregate-standards.md](./aggregate-standards.md)
- **Implement a Handler/Use Case** → See [usecase-standards.md](./usecase-standards.md)
- **Design a REST API** → See [controller-standards.md](./controller-standards.md)
- **Write tests** → See [test-standards.md](./test-standards.md)
- **Handle profile/environment/DI branches** → See [profile-configuration-standards.md](./profile-configuration-standards.md)
- **Handle queries** → See [projection-standards.md](./projection-standards.md)
- **Manage a Read Model** → See [archive-standards.md](./archive-standards.md)

---

## 🛠️ Technology Choices

Database, ORM, event store, message broker, and package versions are determined by target-repository evidence.

This framework may retain conditional/reference guidance for EF Core, Dapper, Npgsql, WolverineFx, RabbitMQ, Kafka, xUnit, NSubstitute, and similar technologies, but a reference selection must not be treated as mandatory truth for every target repository.

---

## 📚 Related Documents

- [Architecture Document](../../ARCHITECTURE.MD) - Overall architecture design
- [Technology Stack Requirements](../../requirement/TECH-STACK-REQUIREMENTS.MD) - Detailed technology-stack requirements
- [ADR Index](../../adr/INDEX.md) - Architecture decision records
- [Code Review Checklist](../CODE-REVIEW-CHECKLIST.md) - Code review checklist

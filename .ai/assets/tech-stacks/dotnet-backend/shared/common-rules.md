# Shared Common Rules (Dotnet)

This file is an agent-loading projection. Normative ownership and precedence are
defined by [AI Context Rule Ownership](../../../../../.dev/standards/AI-CONTEXT-OWNERSHIP.md).

Rule IDs: `TEST-GWT-001`, `TEST-BDDFY-001`, `ARCH-UOW-001`,
`MAP-EVENTS-001`, `DELETE-SOFT-001`, `DELETE-PURGE-001`.

## Execution Summary
1. **DTO rule**: Request/Response DTOs are **separate files** (NOT inner classes).
2. **Testing strategy**: **xUnit + BDDfy is the default profile**; a target team may explicitly decline BDDfy, but all unit, use-case, and integration tests must still use **Given-When-Then structure and naming**, never Arrange-Act-Assert (3A). `.feature` files are optional/planned and supported when supplied, explicitly requested, or enabled by an explicit target profile; **NO BaseTestClass**.
3. **Mocking**: Use **NSubstitute**.
4. **Comments**: Allow **doc comments only** (XML Doc / JSDoc); forbid explanatory inline comments.
5. **Contracts**: Aggregate/UseCase use Contract; Entity/ValueObject/DomainEvent use Objects/Guard.

## ABSOLUTELY FORBIDDEN
- Hardcode environment/profile inside test classes.
- Expose public generic writable CRUD repositories.
- Add query methods to aggregate repositories.
- Use a batch repository for a single-ID operation.
- Use BaseTestClass for tests.
- Add debug output (Console.WriteLine / logging as debugging).
- Mix command/query responsibilities.

## ALWAYS REQUIRED
- If `repo-structure-sync` generated `.dev/project-config.yaml`, use it as a secondary summary of confirmed environment and architecture facts.
- Prefer project files, source types, and deployment configuration when they conflict with generated context.
- Keep controllers thin: map DTOs <-> use cases only.
- Model Use Cases as explicit `I<Operation>UseCase` inbound ports implemented by
  `<Operation>UseCase.ExecuteAsync`.
- Keep Use Case input/output transport-neutral and require a non-optional
  `CancellationToken`.
- Create a Handler only for a real dispatch/message entry; a Handler maps input
  and invokes one Use Case.
- Keep Wolverine conditional. Use Cases depend on project-owned outbound event
  publisher ports, never directly on `IMessageBus` or another Use Case.
- Default query endpoints to query Use Cases. Direct Query Repository/Service
  access is only an explicitly selected pure-query exception.
- Use explicit error handling and return typed results.
- Preserve DDD/CA/CQRS/ES/Outbox concepts from the Java prompts.
- Keep prompt output portable across repositories (see `.ai/assets/shared/PROMPT-PORTABILITY-RULES.md`).
- Use `IAggregateRepository<TAggregate, TId>` for Aggregate Root persistence and
  `IQueryRepository`-derived ports for read models.
- Treat `IDomainRepository<TAggregate, TId>` as a compatibility alias that inherits
  `IAggregateRepository<TAggregate, TId>`.

## Layered Validation Rules
- **Aggregate Root / Use Case**: Contract.require / ensure / invariant
- **Entity / Value Object / Domain Event**: Objects/Guard null checks

## DTO Location Rules
- Directory: `src/Api/Contracts/<Aggregate>/{Requests|Responses}`
- Common: `src/Api/Contracts/Common`
- Naming: `CreateXxxRequest`, `UpdateXxxRequest`, `XxxResponse`, `XxxListResponse`, `ApiErrorResponse`

## Profile / Environment Rules
- Use `ASPNETCORE_ENVIRONMENT` + `appsettings.{Environment}.json`
- Dual-profile test switching only via fixture/collection setup

## Event Sourcing Rules
- Aggregate state changes only via event application (`Apply/When` pattern)
- Events are immutable and carry metadata

## Outbox Rules
- Events are persisted before publishing
- Keep outbox schema consistent with metadata requirements


## EF Core Mapping Completeness (when EF Core is selected)
- Project Decision Slot: Mapping completeness policy (e.g., aggregate roots, owned types, soft-delete behavior).
- All aggregate entities and owned types must be mapped.
- No missing fields in EF Core configurations.
- Collections should use `OwnsMany` or explicit entity mapping.
- Mapping must include soft-delete flags when present.

```csharp
// Example (EF Core)
modelBuilder.Entity<Product>(builder =>
{
    builder.OwnsMany(p => p.Items, items =>
    {
        items.WithOwner().HasForeignKey("ProductId");
        items.Property(i => i.Order).IsRequired();
        // TODO: ensure all fields mapped (no omissions)
    });
});
```

## Serialization / Mapper Rules
- Project Decision Slot: Serialization baseline (enum style, date/time conventions, metadata fields).
- Use a single `JsonSerializerOptions` configuration across the app.
- Enums serialized as strings.
- Date/time types serialized consistently (prefer `DateTimeOffset`).

```csharp
var options = new JsonSerializerOptions
{
    PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
    Converters = { new JsonStringEnumConverter() }
};
```

TODO: finalize mapper rules for domain event serialization and metadata fields.

## Profile-Based DI Examples (illustrative, when these adapters are selected)
- Project Decision Slot: Environment-profile matrix and DI registration strategy.
- Use environment checks to select DI registrations.

```csharp
if (env.IsEnvironment("test-inmemory"))
{
    services.AddDbContext<AppDbContext>(o => o.UseInMemoryDatabase("InMemory"));
}
else if (env.IsEnvironment("test-outbox"))
{
    services.AddDbContext<AppDbContext>(o => o.UseNpgsql(configuration.GetConnectionString("Outbox")));
}
```

TODO: confirm environment names from target-repository evidence and generated project context when present.


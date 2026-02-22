# Shared Common Rules (Dotnet)

## Single Source of Truth (Mandatory Decisions)
1. **DTO rule**: Request/Response DTOs are **separate files** (NOT inner classes).
2. **Testing strategy**: **xUnit + BDDfy with Gherkin-style naming only (no `.feature` files)**; **NO BaseTestClass**.
3. **Mocking**: Use **NSubstitute**.
4. **Comments**: Allow **doc comments only** (XML Doc / JSDoc); forbid explanatory inline comments.
5. **Contracts**: Aggregate/UseCase use Contract; Entity/ValueObject/DomainEvent use Objects/Guard.

## ABSOLUTELY FORBIDDEN
- Hardcode environment/profile inside test classes.
- Create custom repository interfaces for domain operations.
- Use BaseTestClass for tests.
- Add debug output (Console.WriteLine / logging as debugging).
- Mix command/query responsibilities.

## ALWAYS REQUIRED
- Read `project-config.yaml` as the single source of truth for environment and architecture settings.
- Keep controllers thin: map DTOs <-> use cases only.
- Use explicit error handling and return typed results.
- Preserve DDD/CA/CQRS/ES/Outbox concepts from the Java prompts.
- Keep prompt output portable across repositories (see `../PROMPT-PORTABILITY-RULES.md`).

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


## EF Core Mapping Completeness
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

## Profile-Based DI Examples
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

TODO: finalize environment names and ensure they match `project-config.yaml`.

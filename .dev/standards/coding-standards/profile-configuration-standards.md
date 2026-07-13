# Profile / Environment Configuration Standards (.NET)

This document defines mandatory rules for profiles, environments, and profile-specific DI.
It is the authoritative standard for environment loading and profile-specific dependency injection.

Usage tutorials and troubleshooting procedures belong in `.dev/guides/implementation-guides/`; do not mix operational guidance into this standard.

---

## 🔴 Mandatory Rules (MUST FOLLOW)

### 1. The Environment Must Be Determined Only by `DOTNET_ENVIRONMENT` or `ASPNETCORE_ENVIRONMENT`

Do not introduce a custom profile-selection mechanism, such as `.feature` files, custom profile string composition, or hard-coded environment overrides in application code.

```csharp
// ✅ Correct: obtain the current environment from the Host/Builder
var builder = WebApplication.CreateBuilder(args);
var environmentName = builder.Environment.EnvironmentName;

builder.Configuration
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
    .AddJsonFile($"appsettings.{environmentName}.json", optional: true, reloadOnChange: true);
```

```csharp
// ❌ Incorrect: create a separate profile system
var profile = configuration["Profile"] ?? "outbox";
builder.Configuration.AddJsonFile($"appsettings.{profile}.json");
```

### 2. Profile Differences Must Be Stored in `appsettings.{Environment}.json`

Place shared settings in `appsettings.json` and environment differences in `appsettings.{Environment}.json`.
Do not hard-code values for a specific profile back into the base `appsettings.json`.

```json
// ✅ Correct: shared settings
{
  "Repository": {
    "Mode": "InMemory"
  }
}
```

```json
// ✅ Correct: TestOutbox differences appear only in the environment file
{
  "Repository": {
    "Mode": "Outbox"
  },
  "ConnectionStrings": {
    "Outbox": "Host=${DB_HOST};Port=${DB_PORT};Database=${DB_NAME};Username=${DB_USER};Password=${DB_PASSWORD}"
  }
}
```

### 3. Environment Names Must Be Consistent and Predictable

- Use one naming convention; do not mix casing schemes or aliases.
- Current standard names:
  - `Development`
  - `Production`
  - `InMemory`
  - `Outbox`
  - `TestInMemory`
  - `TestOutbox`

```bash
# ✅ Correct
DOTNET_ENVIRONMENT=TestOutbox dotnet test

# ❌ Incorrect: mix a custom profile mechanism with multiple values
DOTNET_ENVIRONMENT=test,test-outbox dotnet test
```

### 4. Profile-Specific DI Must Branch Explicitly at the Composition Root

DI registrations that vary by environment must be centralized in the composition root or a profile-specific registration module.
Do not rely on attribute scanning, automatic assembly scanning, or hidden profile switching inside arbitrary classes.

```csharp
// ✅ Correct: branch centrally at the composition root
if (builder.Environment.IsEnvironment("TestOutbox") || builder.Environment.IsEnvironment("Outbox"))
{
    services.AddDbContext<AppDbContext>(...);
    services.AddScoped<IAggregateRepository<Product, ProductId>, OutboxProductRepository>();
}
else
{
    services.AddSingleton<IAggregateRepository<Product, ProductId>, InMemoryProductRepository>();
}
```

### 5. The InMemory Profile Must Not Register EF Core / Npgsql Dependencies

The InMemory and TestInMemory profiles must start without a DbContext, Npgsql, or a durable outbox.

```csharp
// ❌ Incorrect: the InMemory profile still registers a DbContext
services.AddDbContext<AppDbContext>(...);
```

### 6. The Outbox Profile Must Register the Complete Persistence Chain

The Outbox and TestOutbox profiles must include all of the following:

- DbContext
- Outbox / Wolverine persistence
- the corresponding repository implementation

Partial registration that allows startup to succeed but fails at runtime is prohibited.

### 7. Depend on Abstractions; General Service Constructors Must Not Bind to Profile-Specific Infrastructure Types

```csharp
// ✅ Correct: depend on an abstraction
public sealed class TestDataInitializer
{
    private readonly IAggregateRepository<Product, ProductId> _repository;

    public TestDataInitializer(IAggregateRepository<Product, ProductId> repository)
    {
        _repository = repository;
    }
}
```

```csharp
// ❌ Incorrect: bind directly to specific infrastructure
public sealed class TestDataInitializer
{
    public TestDataInitializer(AppDbContext dbContext)
    {
    }
}
```

### 8. Tests Must Not Mutate Global Environment State Dynamically Inside Test Classes

Select the profile at the test host, fixture, or execution-command layer. Do not override global environment variables directly inside a test class.

---

## Checklist

- [ ] Use only `DOTNET_ENVIRONMENT` / `ASPNETCORE_ENVIRONMENT`.
- [ ] Manage environment differences through `appsettings.{Environment}.json`.
- [ ] Follow the established environment naming convention.
- [ ] Centralize DI profile branches at the composition root.
- [ ] Do not register EF Core / Npgsql in the InMemory profile.
- [ ] Register the complete persistence chain in the Outbox profile.
- [ ] Make general services depend on abstractions rather than profile-specific infrastructure types.
- [ ] Do not modify global environment state inside test classes.

---

## Related Documents

- [../../guides/implementation-guides/PROFILE-CONFIGURATION-COMPLEXITY-SOLUTION.md](../../guides/implementation-guides/PROFILE-CONFIGURATION-COMPLEXITY-SOLUTION.md)
- [../../guides/implementation-guides/DOTNET-DI-TEST-GUIDE.md](../../guides/implementation-guides/DOTNET-DI-TEST-GUIDE.md)
- [../ASPNET-CORE-CONFIGURATION-CHECKLIST.md](../ASPNET-CORE-CONFIGURATION-CHECKLIST.md)

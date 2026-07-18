# Profile-Isolated Configuration Template Set (.NET)

## Purpose
Provides complete .NET DI and configuration templates that fully isolate the InMemory and Outbox profiles to prevent configuration conflicts.

## Canonical Selection Boundary

`DOTNET_ENVIRONMENT` or `ASPNETCORE_ENVIRONMENT` selects the profile. Do not
introduce `Profiles:Mode`, `Repository:Mode`, or another configuration key as a
second selector. Persistence implementations remain target-owned behind the
same application/domain ports.

## 📁 Recommended Configuration Structure

```
src/Infrastructure/Configuration/
├── CommonConfiguration.cs        # Shared by all profiles
├── InMemory/
│   ├── InMemoryConfiguration.cs
│   └── InMemoryProjectionConfig.cs
└── Outbox/
    ├── OutboxInfrastructureConfig.cs
    ├── OutboxRepositoryConfig.cs
    └── OutboxProjectionConfig.cs
```

## 1️⃣ CommonConfiguration (Shared by All Profiles)

```csharp
public static class CommonConfiguration
{
    public static IServiceCollection AddCommonServices(
        this IServiceCollection services)
    {
        services.AddScoped<CreateProductHandler>();
        services.AddScoped<GetProductsHandler>();
        return services;
    }
}
```

## 2️⃣ InMemory Profile Configuration

```csharp
public static class InMemoryConfiguration
{
    public static IServiceCollection AddInMemory(
        this IServiceCollection services, IConfiguration config)
    {
        // Register direct in-memory repository and local transport adapters.
        // Do not register EF Core, Npgsql, or a durable outbox in this profile.
        services.AddSingleton<IProductRepository, InMemoryProductRepository>();
        return services;
    }
}
```

## 3️⃣ Outbox Profile Configuration

```csharp
public static class OutboxConfiguration
{
    public static IServiceCollection AddOutbox(
        this IServiceCollection services, IConfiguration config)
    {
        var conn = config.GetConnectionString("MainDb");
        services.AddDbContext<AppDbContext>(o => o.UseNpgsql(conn));
        // TODO: WolverineFx outbox + message persistence
        return services;
    }
}
```

## 4️⃣ Usage

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddCommonServices();

if (builder.Environment.IsEnvironment("InMemory")
    || builder.Environment.IsEnvironment("TestInMemory"))
{
    builder.Services.AddInMemory(builder.Configuration);
}
else if (builder.Environment.IsEnvironment("Outbox")
    || builder.Environment.IsEnvironment("TestOutbox"))
{
    builder.Services.AddOutbox(builder.Configuration);
}
else
{
    throw new InvalidOperationException(
        $"Unsupported environment '{builder.Environment.EnvironmentName}'.");
}
```

## ⚠️ Important Reminders
- InMemory and Outbox configurations and DI registrations must remain isolated.
- Repository interfaces must remain consistent across profiles.
- WolverineFx and Outbox semantics and event flows must be preserved.

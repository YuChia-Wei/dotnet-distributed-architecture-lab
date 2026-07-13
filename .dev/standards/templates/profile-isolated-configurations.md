# Profile-Isolated Configuration Template Set (.NET)

## Purpose
Provides complete .NET DI and configuration templates that fully isolate the InMemory and Outbox profiles to prevent configuration conflicts.

## 🚨 Important Concept (ezapp 2.0.0 Correspondence)
The two ezDDD/ezapp InMemory and Outbox repository concepts must be preserved in .NET.
For now, implement the corresponding behavior in .NET through custom interfaces and configuration, preserving the concept with TODO markers.

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
        // TODO: InMemory Outbox repository + message storage
        services.AddDbContext<AppDbContext>(o => o.UseInMemoryDatabase("app"));
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

var mode = builder.Configuration["Profiles:Mode"];
if (mode == "InMemory")
{
    builder.Services.AddInMemory(builder.Configuration);
}
else if (mode == "Outbox")
{
    builder.Services.AddOutbox(builder.Configuration);
}
```

## ⚠️ Important Reminders
- InMemory and Outbox configurations and DI registrations must remain isolated.
- Repository interfaces must remain consistent (`findById` / `save` / `delete`).
- WolverineFx and Outbox semantics and event flows must be preserved.

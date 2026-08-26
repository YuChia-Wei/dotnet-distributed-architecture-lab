# Event Architecture Reference (.NET)

## Overview
This document shows how the application switches event propagation by profile
in a Wolverine + EF Core setup.

## Architecture Comparison

```
InMemory profile:
Repository.save() -> InMemory Transport -> Reactors/Handlers

Outbox profile:
Repository.save() -> PostgreSQL (outbox) -> Wolverine outbox relay
                  -> Message Broker -> Reactors/Handlers
```

## Program.cs (Profile-aware bootstrap)

```csharp
var builder = WebApplication.CreateBuilder(args);
var env = builder.Environment;

if (env.IsEnvironment("Outbox") || env.IsEnvironment("TestOutbox"))
{
    builder.Services.AddPlanDataSource(builder.Configuration);
    builder.Services.AddOutboxRepositories(builder.Configuration);
    // Wolverine durable outbox setup (TODO)
}
else
{
    // InMemory configuration (no EF Core, no DB)
    // Register in-memory repositories and local transport
}
```

## Profile Detection Pattern

Use the host environment name to switch. Do not introduce a configuration-key
selector such as `Repository:Mode`:

```csharp
if (builder.Environment.IsEnvironment("Outbox")
    || builder.Environment.IsEnvironment("TestOutbox"))
{
    // outbox setup
}
```

## Common Pitfalls

- Registering EF Core for InMemory profile (causes unwanted DB setup).
- Mixing InMemory transport with outbox-only components.
- Forgetting to configure Wolverine outbox when using PostgreSQL.

## Required Reading
- `inmemory-profile-config.md`
- `outbox-profile-config.md`

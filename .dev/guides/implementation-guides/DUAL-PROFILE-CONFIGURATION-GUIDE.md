# Dual-Profile Configuration Guide (Dotnet)

## Overview
This guide explains how to configure dual profiles in a .NET application to support InMemory and Outbox modes.

## Problem Background

### Common mistakes
- Using a single `appsettings.json` for all profiles
- InMemory mode still tries to connect to a database
- Tests cannot switch profiles reliably

### Sub-agent misunderstanding of "inmemory"
- Generating SQLite/H2 style code
- ezapp 2.0.0 intent: use OutboxRepository semantics with InMemory store + InMemory message DB

## Correct Configuration Structure

### 1. appsettings.json (shared)
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information"
    }
  }
}
```

Note: set the environment via `ASPNETCORE_ENVIRONMENT` (or launchSettings). Do not hardcode it inside appsettings.

### 2. appsettings.inmemory.json
```json
{
  "Data": {
    "DisableEfCore": true
  }
}
```

### 3. appsettings.outbox.json
```json
{
  "ConnectionStrings": {
    "Outbox": "Host=localhost;Port=5500;Database=board;Username=postgres;Password=root"
  }
}
```

### 4. appsettings.test-inmemory.json
```json
{
  "Data": {
    "DisableEfCore": true
  },
  "Logging": {
    "LogLevel": {
      "Default": "Warning"
    }
  }
}
```

### 5. appsettings.test-outbox.json
```json
{
  "ConnectionStrings": {
    "Outbox": "Host=localhost;Port=5800;Database=board_test;Username=postgres;Password=root"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Warning"
    }
  }
}
```

## Profile-specific DI registration

### InMemory profile (ezapp 2.0.0 intent)
```csharp
if (env.IsEnvironment("inmemory") || env.IsEnvironment("test-inmemory"))
{
    services.AddInMemoryProfile();
    // TODO: ensure InMemory store + message DB + broker are registered
}
```

### Outbox profile
```csharp
if (env.IsEnvironment("outbox") || env.IsEnvironment("test-outbox"))
{
    services.AddDbContext<AppDbContext>(o =>
        o.UseNpgsql(configuration.GetConnectionString("Outbox")));

    services.AddWolverine(opts =>
    {
        opts.PersistMessagesWithPostgresql(configuration.GetConnectionString("Outbox"));
        opts.UseDurableOutbox();
    });
}
```

## Test configuration

- Use xUnit fixtures (no BaseTestClass).
- Profiles switch only via `ASPNETCORE_ENVIRONMENT`.

### Environment selection
```bash
ASPNETCORE_ENVIRONMENT=test-inmemory dotnet test
ASPNETCORE_ENVIRONMENT=test-outbox dotnet test
```

## Verification

### 1. Verify InMemory profile
```bash
ASPNETCORE_ENVIRONMENT=inmemory dotnet run
# Expected:
# - app starts on {backendPort}
# - no database connection attempts
# - logs contain no EF Core startup
```

### 2. Verify Outbox profile
```bash
ASPNETCORE_ENVIRONMENT=outbox dotnet run
# Expected:
# - app starts on {backendPort}
# - PostgreSQL connected at localhost:5500
# - Wolverine outbox enabled
```

### 3. Verify tests
```bash
ASPNETCORE_ENVIRONMENT=test-inmemory dotnet test
ASPNETCORE_ENVIRONMENT=test-outbox dotnet test
```

## FAQ

### Q1: Tests still attempt DB in InMemory
Cause: EF Core registered unconditionally
Fix: guard DbContext registration with environment checks

### Q2: Profile switching not working
Cause: environment hardcoded in code
Fix: use `ASPNETCORE_ENVIRONMENT` and appsettings.*.json

### Q3: DI conflicts
Cause: service registrations collide between profiles
Fix: keep registrations separated and use consistent service types

## Sub-agent Notes

When using command-sub-agent or other workflows:
1. Be explicit about profile meaning:
   - inmemory = OutboxRepository semantics + InMemory store + InMemory message DB
   - outbox = OutboxRepository + PostgreSQL + Wolverine durable outbox
2. Reject SQLite/H2 code for inmemory
3. Tests must not set environment inside test classes

This configuration keeps profile switching reliable and avoids DB conflicts.

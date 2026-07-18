# Complete ASP.NET Core Setup Guide (Based on .NET Stack)

## ⚠️ IMPORTANT NOTICE
This guide adapts the source stack setup to .NET (ASP.NET Core + WolverineFx + EF Core).
All architecture rules and profiles must be preserved.

## 🎯 Purpose
Provide a **complete, working** .NET setup that mirrors the source stack behavior:
- Profiles (inmemory / outbox)
- CQRS + Event Sourcing
- Outbox pattern

## 🔥 Quick Start

### 1. Solution layout
Use the conditional profile in `project-structure.md` only when target repository
evidence or an explicit team decision adopts it. Otherwise preserve the target's
observed layout and record unresolved structure through `repo-structure-sync`.

### 2. Core packages
- WolverineFx (CQRS / Messaging)
- EF Core + provider (Npgsql/SqlServer)
- xUnit + BDDfy (Gherkin-style naming only)
- Target `testing.mocking` selection (NSubstitute by default)

### 3. Configuration
Use `appsettings.json` and `appsettings.{Environment}.json`.

Example:
```json
{
  "ConnectionStrings": {
    "MainDb": "Host=${DB_HOST};Port=${DB_PORT};Database=${DB_NAME};Username=${DB_USER};Password=${DB_PASSWORD}"
  },
  "Outbox": {
    "Enabled": true
  }
}
```

Select `Outbox` through `DOTNET_ENVIRONMENT` or `ASPNETCORE_ENVIRONMENT`; the
configuration document does not select its own profile.

### 4. Outbox / Event Sourcing
- Configure WolverineFx with persistence/outbox
- Ensure messages/events are stored reliably

## 📦 Reference Templates
- `.dev/standards/templates/`
- `.dev/standards/examples/`

## TODO
- Replace placeholders with concrete EF Core + Wolverine configuration once examples are translated.

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
Use the structure in `project-structure.md`.

### 2. Core packages
- WolverineFx (CQRS / Messaging)
- EF Core + provider (Npgsql/SqlServer)
- xUnit + BDDfy (Gherkin-style naming only)
- NSubstitute

### 3. Configuration
Use `appsettings.json` and `appsettings.{Environment}.json`.

Example:
```json
{
  "ConnectionStrings": {
    "MainDb": "Host=localhost;Port=5432;Database=app;Username=app;Password=app"
  },
  "Profiles": {
    "Mode": "outbox"
  }
}
```

### 4. Outbox / Event Sourcing
- Configure WolverineFx with persistence/outbox
- Ensure messages/events are stored reliably

## 📦 Reference Templates
- `.dev/standards/templates/`
- `.dev/standards/examples/`

## TODO
- Replace placeholders with concrete EF Core + Wolverine configuration once examples are translated.

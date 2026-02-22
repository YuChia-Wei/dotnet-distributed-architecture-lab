# ASP.NET Core Configuration Examples

This directory contains ASP.NET Core templates for new projects using
Wolverine + EF Core + ezDDD-style patterns.

## Files Overview

1. `Program.cs`
   - Minimal hosting bootstrap
   - Profile-based wiring
   - Outbox relay setup (TODO)

2. `InMemoryRepositoryConfig.cs`
   - InMemory profile registrations
   - No database dependencies

3. `OutboxRepositoryConfig.cs`
   - Outbox profile registrations
   - PostgreSQL + EF Core + Wolverine

4. `UseCaseConfiguration.cs`
   - Use case and projection registrations

5. `appsettings*.json`
   - Base configuration + profile-specific overrides

## Usage Guide

1. Copy files into your project:
   - C# files -> `src/{YourProject}/`
   - JSON files -> `appsettings*.json`

2. Replace placeholders:
   - `{rootNamespace}` -> your root namespace

3. Select a profile:
   - Development/Testing: `InMemory`
   - Production: `Outbox`

## Notes

- Keep EF Core registration **only** in Outbox profile.
- Do not use source-stack framework concepts in .NET templates.
- Keep ezDDD/ezSpec intent intact.

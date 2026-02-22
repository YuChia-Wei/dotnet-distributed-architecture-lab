# Examples (.NET)

This directory contains .NET examples and templates used by the AI coding
assistant for the Clean Architecture + DDD + CQRS stack.

## Verified Templates (Single Source of Truth)

### `examples/nuget/`
Verified NuGet dependency templates.
Use placeholders and version sources from `.dev/project-config.yaml`.

### `examples/aspnet-core/`
Verified ASP.NET Core configuration templates:
- `Program.cs`
- `appsettings.*.json`
- profile-based wiring

### `examples/generation-templates/`
Full module templates used for code generation.

## Directory Highlights

- `contract/` - Design by Contract docs and examples
- `projection/` - Read model/projection patterns
- `usecase/` - Use case interfaces + services
- `test/` - BDDfy + xUnit patterns (Gherkin-style naming)
- `bdd-gherkin-example/` - Reqnroll `.feature` examples (reference only)
- `bdd-gherkin-test/` - Reqnroll `.feature` test patterns (reference only)
- `reference/` - Reference docs

## Contract Quick Reference

```csharp
Contract.RequireNotNull("param", param);
Contract.Require(condition, "reason");
Contract.Ensure(condition, "reason");
Contract.Invariant(condition, "reason");
```

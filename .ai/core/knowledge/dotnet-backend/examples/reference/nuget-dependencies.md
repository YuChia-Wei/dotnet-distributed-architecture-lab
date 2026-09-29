# NuGet Dependencies Reference (.NET)

This list captures the expected dependency groups for the .NET stack.
Pick exact package names and versions based on your project needs.

## Core Architecture

- Wolverine/WolverineFx (CQRS, messaging, outbox) when selected
- EF Core (ORM) or Dapper (read-side/data-access adapter) when selected
- Npgsql EF Core provider (PostgreSQL) when EF Core and PostgreSQL are selected

## Contract / DDD Utilities

- Use a target-selected guard/contract mechanism or focused Domain tests to
  implement DbC semantics; this framework selects no contract package.

## Testing

- xUnit (`xunit`, `xunit.runner.visualstudio`, `Microsoft.NET.Test.Sdk`)
- BDDfy (`TestStack.BDDfy`) for BDD (Gherkin-style naming)
- Gherkin runner (Reqnroll) is optional and used only for reference examples
- LightBDD is an owner-named evaluation candidate, not a selected profile dependency
- NSubstitute (mocking)

## Optional (Common)

- FluentAssertions (assertions)
- coverlet.collector (code coverage)

## Example (Package Groups)

```text
Wolverine
Microsoft.EntityFrameworkCore
Npgsql.EntityFrameworkCore.PostgreSQL
xunit
xunit.runner.visualstudio
Microsoft.NET.Test.Sdk
TestStack.BDDfy
Reqnroll (optional, reference-only)
NSubstitute
```

## Latest Version Snapshot (2026-02-22, from current `*.csproj`)

- WolverineFx: 5.16.2
- WolverineFx.Kafka: 5.16.2
- WolverineFx.RabbitMQ: 5.16.2
- Dapper: 2.1.66
- Npgsql: 10.0.1
- Microsoft.AspNetCore.OpenApi: 10.0.3
- xunit: 2.9.3
- xunit.runner.visualstudio: 3.1.5
- Microsoft.NET.Test.Sdk: 18.0.1
- Shouldly: 4.3.0
- Moq: 4.20.72
- coverlet.collector: 8.0.0
- OpenTelemetry.Extensions.Hosting: 1.15.0
- RabbitMQ.Client.OpenTelemetry: 1.0.0-rc.1

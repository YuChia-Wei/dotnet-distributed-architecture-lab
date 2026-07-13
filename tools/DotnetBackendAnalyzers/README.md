# Dotnet Backend Analyzers

Source-included Roslyn analyzer template for this AI context framework's .NET backend profile.

Current diagnostics:

- `DBA1001` (error): enforces semantic aggregate/query repository boundaries,
  compatibility inheritance, Aggregate Root constraints, the portable two-method
  aggregate contract, and the prohibition on public generic writable CRUD ports.
- `DBA1002` (error): use cases or handlers must not inject `IServiceProvider`.
- `DBA1003`: aggregates/entities should not reference infrastructure types such as `DbContext`.
- `DBA1004`: concrete controller classes should declare `ApiControllerAttribute`.
- `DBA1005` (error): controllers must not reference `DbContext` or call `SaveChanges`.
- `DBA1006` (error): controllers must not directly construct Handler or Use Case types.
- `DBA1007`: object mappers should be static classes.
- `DBA1008`: object mappers should not depend on repositories, use cases, or handlers.
- `DBA1009`: event-sourced aggregate state should mutate only inside `When` transitions.
- `DBA1010` (error): use cases must not use service locator or attribute-based property injection.
- `DBA1011` (error): handlers must not mix command and query marker responsibilities.
- `DBA1012` (error): use cases must not directly construct repositories.
- `DBA1013`: projection services should not call EF persistence write operations.
- `DBA1014` (error): controllers must not inject concrete Handlers, buses,
  dispatchers, write repositories, or Domain services. Query repositories/services
  remain available for an explicitly selected pure-query endpoint.
- `DBA1015` (error): Use Case contracts and implementations must use
  `ExecuteAsync`, a non-optional `CancellationToken`, and transport-neutral input;
  a Use Case must not also expose `Handle`/`HandleAsync`.
- `DBA1016` (error): Use Cases must not inject `IMessageBus`, a mediator/
  dispatcher, or another Use Case.
- `DBA1017` (error): `*CommandHandler` and `*QueryHandler` types must adapt to
  exactly one Use Case and must not depend on repositories or Domain services.

`DBA1001` replaces the former repository grep compliance scripts. It classifies
canonical, compatibility, and derived ports through interface inheritance rather
than broad `Repository` name matching. Target-specific batch ports are intentionally
outside this portable analyzer.

`DBA1004` through `DBA1006` replace the former controller grep compliance script.
`DBA1007` and `DBA1008` replace the former mapper grep compliance scripts.
`DBA1014` through `DBA1017` enforce the deterministic portion of the approved Use
Case inbound-port and Handler adapter model. Whether a pure-query endpoint was
explicitly selected remains target-repository evidence and is not inferred from
orchestration quality.

Analyzers do not replace AI software engineering reasoning context used by review and architecture skills.

## Run Tests

```bash
dotnet test tools/DotnetBackendAnalyzers.Tests/DotnetBackendAnalyzers.Tests.csproj
```

## Source-Included Usage Direction

For now this project is intended to travel with the AI context framework as source. Do not package it as NuGet until the rules and AI skill integration stabilize.

## Wire Into A Target Repo

After copying this analyzer source into a target repo, wire it into target projects through `Directory.Build.props`.

Use:

- `templates/Directory.Build.props.snippet`
- `templates/analyzer-severity.editorconfig`

The snippet adds the analyzer project as a `ProjectReference` with:

- `OutputItemType="Analyzer"`
- `ReferenceOutputAssembly="false"`
- `PrivateAssets="all"`

This lets target projects receive analyzer diagnostics during `dotnet build` without referencing the analyzer as a runtime assembly.

The severity template keeps each architecture diagnostic independently configurable. Target repositories may use `none`, `suggestion`, `warning`, or `error` according to their architecture profile and team agreement.

Custom DBA diagnostics run during build after the analyzer project is wired in. Standard IDE coding-style preferences may additionally require `EnforceCodeStyleInBuild`, `dotnet format --verify-no-changes`, or an equivalent CI command. A warning blocks the build only when warnings are treated as errors.

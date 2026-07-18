# Persistence Configuration Guide

本文件定義 ORM / persistence configuration 在 repo 中的建議落點與責任邊界。

## 核心規則

- `DbContext`
- EF Core configurations
- connection-string-oriented persistence setup
- migration-related persistence registration

都應放在：

- `Infrastructure/Persistence`

或其明確子區域，例如：

- `Infrastructure/Configuration/Persistence`

## Why

- ORM 屬於 persistence concern，不是 Web concern
- Web / API 層應只保留 transport、middleware、endpoint concern
- 將 persistence 配置集中在 Infrastructure，可避免層級語意混亂

## Recommended Placement

```text
<Domain>.Infrastructure/
  Persistence/
    <Domain>DbContext.cs
    Configurations/
    Migrations/
```

若專案規模需要更細分，可採：

```text
<Domain>.Infrastructure/
  Configuration/
    Persistence/
```

但不要把 DbContext / EF Core configuration 放回 WebApi 專案。

## Practical Rule

- WebApi:
  - host startup, middleware, controller, transport adapter
- Infrastructure/Persistence:
  - DbContext, EF Core mapping, persistence registration

## EF Core Registration Profile

Use this section only when the target's `persistence.orm` selection is EF Core.
The Domain and Application layers must not depend on `DbContext`.

```csharp
builder.Services.AddDbContext<AppDbContext>(options =>
{
    var connectionString =
        builder.Configuration.GetConnectionString("Main");
    options.UseNpgsql(connectionString);
});

services.AddScoped<IPlanProjection, EfPlanProjection>();
services.AddScoped<IPlanArchive, EfPlanArchive>();
```

The provider call is illustrative. Replace `UseNpgsql` with the provider chosen
by the target repository.

Register every selected Repository, Projection, Inquiry, and Archive adapter in
Infrastructure. Keep InMemory and database-backed registrations isolated by
the target's selected profile so a test-only profile does not connect to a real
database.

## Validation

```bash
dotnet test tools/DotnetBackendValidation.Tests/DotnetBackendValidation.Tests.csproj
```

When the target uses the supplied validation pattern, it provides an
`IProjectionReadModel` marker and uses
`ProjectionModelRegistrationValidator` to compare marker implementations with
the assembled EF Core model.

Checklist:

- Repository, Projection, Inquiry, and Archive adapters are registered.
- `DbContext` and provider APIs remain in Infrastructure.
- Read-only projections use `AsNoTracking` when applicable.
- Controllers and Domain types do not depend on `DbContext`.

## Related

- `../../standards/project-structure.md` (conditional target layout; confirm adoption before applying physical paths)
- `../../standards/coding-standards.md`
- `DATABASE-MIGRATION-GUIDE.md`
- `PREVENT-SERVICE-REGISTRATION-MISSING.md`
- `../../standards/TECHNOLOGY-SELECTION-POLICY.md`

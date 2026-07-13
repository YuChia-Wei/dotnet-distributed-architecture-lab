# EF Core Configuration Guide

## 🎯 Core Principles

All EF Core-related Repository/Projection/Inquiry/Archive implementations must be registered correctly in DI
and preserve DDD/CA/CQRS layering: Domain does not depend on EF Core, and only Infrastructure may use DbContext.

## 📦 Recommended Structure

```
src/Infrastructure/
├── Repositories/Outbox/
├── Projections/
├── Inquiry/
└── Archive/
```

## 🔧 DbContext Configuration

```csharp
builder.Services.AddDbContext<AppDbContext>(options =>
{
    var conn = builder.Configuration.GetConnectionString("MainDb");
    options.UseNpgsql(conn);
});
```

## 🧩 DI Registration Rules

- Repository / Projection / Inquiry / Archive must all be registered in DI
- Register DbContext only in Infrastructure
- Domain and Application must not depend directly on DbContext

```csharp
services.AddScoped<IPlanProjection, EfPlanProjection>();
services.AddScoped<IPlanArchive, EfPlanArchive>();
```

## ⚠️ Common Issues

### Issue 1: Unable to Resolve a Service
**Error message**:
```
Unable to resolve service for type 'EfPlanProjection'
```

**Solution**:
- Confirm that the class is registered in DI
- Confirm that the namespace matches assembly scanning

### Issue 2: Duplicate Registration
**Symptom**: Multiple implementations cause conflicts

**Solution**:
- Map each interface to only one implementation
- Isolate InMemory/Outbox registrations by profile

## 🔍 Automated Check

```bash
dotnet test tools/DotnetBackendValidation.Tests/DotnetBackendValidation.Tests.csproj
```

The target repository should provide an `IProjectionReadModel` marker interface and use
`ProjectionModelRegistrationValidator` to compare marker implementations with the assembled `DbContext.Model`.

## 📋 Checklist

- [ ] Repository/Projection/Inquiry/Archive are registered
- [ ] DbContext is used only in the Infrastructure layer
- [ ] Projections use AsNoTracking
- [ ] Controllers do not depend directly on DbContext

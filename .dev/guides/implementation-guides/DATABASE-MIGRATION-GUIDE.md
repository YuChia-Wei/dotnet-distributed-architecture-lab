# Database Migration Guide (.NET)

## 📋 Overview
This guide describes database migration strategies and best practices for .NET, with stability, safety, and rollback capability as its goals.

## 🎯 Migration Strategy

### Tool Selection

Use the target repository's selected persistence technology. When
`persistence.orm` selects EF Core, EF Core Migrations is the default approach
for development, testing, and production. DbUp, Flyway, or another migration
tool requires an explicit target selection and operating model.

```
Development environment: EF Core Migrations
Test environment: EF Core Migrations + Testcontainers
Production environment: EF Core Migrations (generate and review SQL first)
```

## 🛠️ EF Core Migrations Configuration

### 1. Required Packages
```bash
dotnet add package Microsoft.EntityFrameworkCore
dotnet add package Microsoft.EntityFrameworkCore.Design
dotnet add package <Selected-EF-Core-Provider>
```

### 2. Directory Structure (Recommended)
```
<Workload>.Infrastructure/
└── Migrations/
    ├── 202401010900_InitialCreate.cs
    ├── 202401011030_AddUserTable.cs
    └── ...
```

### 3. Basic Commands
```bash
# Create a migration
dotnet ef migrations add InitialCreate --project <InfrastructureProject> --startup-project <HostProject>

# Apply migrations
dotnet ef database update --project <InfrastructureProject> --startup-project <HostProject>

# Generate SQL (review before deployment is recommended)
dotnet ef migrations script --project <InfrastructureProject> --startup-project <HostProject> -o migration.sql
```

## 🔄 Migration Procedure

### 1. Development/Testing
```bash
dotnet ef migrations add <MigrationName> --project <InfrastructureProject> --startup-project <HostProject>
dotnet ef database update --project <InfrastructureProject> --startup-project <HostProject>
```

### 2. Production Environment (Recommended)
```bash
# Generate SQL, then execute it after manual review
dotnet ef migrations script --project <InfrastructureProject> --startup-project <HostProject> -o release.sql
```

## 🔁 Rollback Strategy

### EF Core Rollback
```bash
# Return to the previous migration
dotnet ef database update <PreviousMigration> --project <InfrastructureProject> --startup-project <HostProject>

# Return to the initial state (testing/development only)
dotnet ef database update 0 --project <InfrastructureProject> --startup-project <HostProject>
```

## 🎨 Best Practices

1. **Do not use EnsureCreated/EnsureDeleted in production**
2. **Generate and review SQL before deployment**
3. **Use explicit names (including a time prefix)**
4. **Provide a rollback strategy for significant changes**
5. **Outbox / Event Store schemas must be included in migrations**

## 📊 Monitoring and Health Checks

### Pending migrations
```csharp
public sealed class MigrationHealthCheck : IHealthCheck
{
    private readonly AppDbContext _db;
    public MigrationHealthCheck(AppDbContext db) => _db = db;

    public Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context, CancellationToken token = default)
    {
        var pending = _db.Database.GetPendingMigrations().ToList();
        return Task.FromResult(pending.Count == 0
            ? HealthCheckResult.Healthy()
            : HealthCheckResult.Degraded($"Pending migrations: {pending.Count}"));
    }
}
```

## 📋 Checklist

### Before Migration
- [ ] Create a complete database backup
- [ ] Validate in the test environment
- [ ] Prepare a rollback plan

### After Migration
- [ ] Verify application functionality
- [ ] Check pending migrations
- [ ] Monitor performance metrics

## Related

- [Persistence configuration](PERSISTENCE-CONFIGURATION-GUIDE.md)
- [Technology selection policy](../../standards/TECHNOLOGY-SELECTION-POLICY.md)
- [Project structure](../../standards/project-structure.md)

# Outbox Pattern Test Configuration (.NET)

## Overview
This guide describes how to configure and run Outbox pattern integration tests.

## 1. Profile Configuration

Outbox tests use `Test.Outbox` profile:
- `appsettings.Test.Outbox.json`

Example (connection string):
```json
{
  "ConnectionStrings": {
    "OutboxDb": "Host=localhost;Port=5800;Database=board;Username=postgres;Password=root"
  }
}
```

Notes:
- Use PostgreSQL on port 5800
- Schema: `message_store` (if required)

## 2. Test Host Configuration

In your fixture, switch services based on profile:
```csharp
if (ActiveProfile == TestProfiles.Outbox)
{
    // EF Core: UseNpgsql(connectionString)
    // Wolverine: Use outbox + durable messaging
}
```

Avoid base test classes; use fixtures and DI instead.

## 3. Required Test Cases

Every OutboxRepository must include these scenarios:

1. **Persist data**  
   Verify all fields are saved, including JSON columns.
2. **Retrieve data**  
   Verify rehydration is complete and correct.
3. **Soft delete**  
   Use `Save()` to mark `IsDeleted = true`, not hard delete.
4. **Version control**  
   Verify optimistic locking version increments.

## 4. Database Assertions

Use EF Core or raw SQL for direct checks:
```csharp
var isDeleted = await db.Database
    .SqlQueryRaw<bool>("SELECT is_deleted FROM message_store.product WHERE id = {0}", id)
    .SingleAsync();
```

## FAQ

### Why no base test classes?
To keep configuration explicit and readable. Use fixtures + helpers instead.

### How to share helpers?
Use composition:
```csharp
public sealed class OutboxTestHelper
{
    public Task VerifyDataAsync(/* ... */) => Task.CompletedTask;
}
```

## Checklist

- [ ] Use `Test.Outbox` profile
- [ ] PostgreSQL running on port 5800
- [ ] `IsDeleted` verified via `Save()` (soft delete)
- [ ] Version increment verified

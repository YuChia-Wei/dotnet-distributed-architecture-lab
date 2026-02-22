# Outbox Profile Configuration (.NET)

## Purpose
Reference configuration for Outbox profile, using PostgreSQL and Wolverine outbox.

## Event Flow
```
Repository.save() -> PostgreSQL (outbox) -> Wolverine relay -> Broker -> Reactors/Handlers
```

## Example Configuration

```csharp
builder.Services.AddPlanDataSource(builder.Configuration);
builder.Services.AddOutboxRepositories(builder.Configuration);

builder.Services.AddWolverine(opts =>
{
    // TODO: configure PostgreSQL persistence + outbox
    // opts.PersistMessagesWithPostgresql(connectionString);
    // opts.UseDurableOutbox();
});
```

## Key Points

- DbContext and PostgreSQL are REQUIRED.
- Outbox relay must be enabled.
- Do NOT register in-memory transport for this profile.

## App Settings

`appsettings.Outbox.json` should include DB + outbox settings:

```json
{
  "Repository": {
    "Mode": "outbox"
  },
  "ConnectionStrings": {
    "PlanDb": "Host=localhost;Port=5500;Database=board;Username=postgres;Password=root"
  },
  "Outbox": {
    "Enabled": true
  }
}
```

## Validation Checklist
- [ ] DbContext registered
- [ ] Outbox relay enabled
- [ ] Message broker configured
- [ ] No MessageBus-only in-memory pipeline

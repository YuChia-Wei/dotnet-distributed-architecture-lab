# InMemory Profile Configuration (.NET)

## Purpose
Reference configuration for InMemory profile, showing direct event propagation
without a database.

## Event Flow
```
Repository.save() -> InMemory transport -> Reactors/Handlers
```

## Example Configuration

```csharp
builder.Services.AddSingleton<IMessageBus, InMemoryMessageBus>();
builder.Services.AddScoped<IRepository<Plan, PlanId>, InMemoryPlanRepository>();
```

## Key Points

- Do NOT register EF Core or DbContext.
- Do NOT register outbox relay components.
- Use in-memory repositories or outbox + in-memory ORM equivalents (TODO).

## App Settings

`appsettings.InMemory.json` should disable DB and outbox:

```json
{
  "Repository": {
    "Mode": "inmemory"
  },
  "Outbox": {
    "Enabled": false
  }
}
```

## Validation Checklist
- [ ] No DbContext registrations
- [ ] No outbox relay services
- [ ] InMemory transport configured
- [ ] Repositories wired for in-memory mode

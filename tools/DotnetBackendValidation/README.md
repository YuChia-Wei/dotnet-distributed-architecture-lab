# Dotnet Backend Validation

Source-included runtime and configuration validation helpers for rules that cannot be proven by a Roslyn analyzer.

## Projection Model Registration

`ProjectionModelRegistrationValidator.FindUnregistered` discovers concrete types that implement the target repository's projection read-model marker interface and reports those absent from the assembled EF Core model.

The production marker interface belongs in the target repository's shared query/read-model building blocks, not in this validation project. The recommended name is `IProjectionReadModel`.

Example target-repository test:

```csharp
var missing = ProjectionModelRegistrationValidator.FindUnregistered(
    typeof(IProjectionReadModel).Assembly.GetTypes(),
    typeof(IProjectionReadModel),
    type => dbContext.Model.FindEntityType(type) is not null);

Assert.Empty(missing);
```

Dapper-only DTOs and query services should not implement the marker interface.

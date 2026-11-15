# Target-Owned Projection Registration Test Recipe

Evidence tier: `reference-only`.

When a target uses EF Core projection read models, it may define a marker such
as `IProjectionReadModel` in its own shared query-model contracts and add a
configuration test against the assembled target model. Dapper-only DTOs and
query services should not implement the EF registration marker.

```csharp
var marker = typeof(IProjectionReadModel);
var projectionTypes = marker.Assembly.GetTypes()
    .Where(type => type.IsClass && !type.IsAbstract)
    .Where(type => marker.IsAssignableFrom(type));

var missing = projectionTypes
    .Where(type => dbContext.Model.FindEntityType(type) is null)
    .ToArray();

Assert.Empty(missing);
```

The target owns assembly selection, reflection filtering, EF Core and test
package versions, `DbContext` construction, exclusions, command invocation, and
fresh evidence. This bounded pattern does not prove registration in any target
and does not require a framework runtime-validation project.

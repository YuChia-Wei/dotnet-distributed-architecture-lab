# Persistence configuration

Use the target's selected persistence and architecture. Inspect project files,
provider packages, registration and deployed settings to confirm actual ORM,
connection, schema and migration ownership. Each bounded context can choose a
different provider.

## Ownership

The Infrastructure persistence module owns provider APIs, connection setup,
schema/model configuration and migration registration. In an adopted layered
layout this may be `<Domain>.Infrastructure/Persistence`, with a selected
`DbContext`, mappings and migrations. The host composition root invokes that
module and owns host, middleware and endpoint settings. Domain and Application
depend on their selected ports, and HTTP transport code does not own ORM setup.

Resolve each selected Repository, Projection, Inquiry or Archive abstraction to
the appropriate provider registration. Check lifetimes, the selected connection
and actual schema. A pure mapper takes explicit values and does not need DI.
Use target-specific startup validation to expose a missing dependency or a
partial registration chain.

## Conditional provider checks

| Selected adapter | Check |
| --- | --- |
| EF Core | Provider and matching configuration, correct tracking/no-tracking and async materialization, model coverage, concurrency tokens, connection, schema and migration ownership |
| Dapper or direct SQL | Parameterization, connection/transaction lifetime, mapping completeness, optimistic version predicates, atomic multi-statement and batch semantics |
| Event store | Expected version, append-only persistence, replay/snapshot policy, and acknowledgement after a successful append under the selected aggregate contract |
| Other durable adapter | Actual configuration, version/transaction semantics and compatible read/write registrations |
| In-memory adapter | Lifetime, isolation and reset behavior, with only the infrastructure needed by the selected contract |

Use the [migration guide](database-migrations.md) for the selected migration
mechanism. If the target requires EF model registration validation, the
[reference-only recipe](../../tooling/on-demand-mechanical-validation/recipes/projection-registration-test.md)
compares selected concrete read models to the assembled model. The target owns
the marker, validation project, runtime and evidence.

## Adopted dual-persistence profile

The original dual profile uses `InMemory` and `TestInMemory` without a
`DbContext`, Npgsql or a durable outbox. `Outbox` and `TestOutbox` require the
full selected chain: DbContext, Outbox/Wolverine persistence and matching
repository implementations. A different adopted durable adapter follows its
own target contract and does not acquire that dependency list from its name.

Branch explicitly at host composition, using the resolved environment and
[exact profile names](../../core/host-configuration.md). The following shows
the control flow for a target that already owns the two registration modules:

```csharp
if (builder.Environment.IsEnvironment("Outbox") ||
    builder.Environment.IsEnvironment("TestOutbox"))
{
    var connection = builder.Configuration.GetConnectionString("Outbox")
        ?? throw new InvalidOperationException("Missing Outbox connection string.");
    builder.Services.AddOutboxPersistence(connection);
}
else if (builder.Environment.IsEnvironment("InMemory") ||
         builder.Environment.IsEnvironment("TestInMemory"))
{
    builder.Services.AddInMemoryPersistence();
}
```

The module names are illustrative. Resolve other supported environments to
their accepted defaults or fail clearly for an unsupported configuration.
Validate the complete selected provider chain and keep the fast profile isolated
from database access. Check [each selected profile](../../testing/profile-based-testing.md)
and apply [transaction ownership](../messaging/transactional-messaging-standards.md)
where state and outgoing intent share a durable operation.

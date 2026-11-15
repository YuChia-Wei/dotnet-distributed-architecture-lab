# Troubleshooting selected .NET behavior

Trace the failing scenario from the actual entry point through the selected
configuration, adapter and observation boundary. Establish the target versions,
profile and first failing step before proposing a change.

| Symptom | Distinguishing checks |
| --- | --- |
| A type such as `IDomainEvent` fails to resolve | Verify the target namespace, project reference and actual type definition. Compare the portable and optional ES types in [reconstruction](../architecture/ddd-cqrs/building-blocks-reconstruction.md). |
| A service cannot be resolved, or the wrong provider starts | Follow the constructor's abstraction to its registration and module, then inspect which host environment branch actually ran, whether the adapter's dependencies are registered, and whether the lifetime is compatible. See [persistence configuration](../integration/persistence/configuration.md). |
| Startup works but a database operation fails | Check the actual connection source, database/port, schema and migration status under the selected host profile. Inspect generated SQL and deployment evidence with the [migration guide](../integration/persistence/database-migrations.md). |
| Round trip drops required state or historical data fails | Compare columns/serialized members, discriminators, schema version and trace metadata against the real payload. Check that malformed required fields fail visibly and that ordinary and event-sourced reconstruction follow the selected contract. See [mapping](../integration/persistence/mapper-standards.md). |
| A delivery, reactor or recorded event is missing | Check that the producer used the intended event identity, the handler was registered for that identity, and the test awaited capture. For a durable path distinguish local commit, pending acknowledgement and actual delivery. See [reactors](../architecture/ddd-cqrs/reactor-standards.md) and [transactional messaging](../integration/messaging/transactional-messaging-standards.md). |
| A scenario passes without exercising behavior | Verify runner discovery, non-empty BDDfy steps where adopted, supplied row/argument binding, and an awaited real When. A mock of the subject, unawaited asynchronous operation or assertion on fixture setup can hide the failure. See [test standards](../testing/test-standards.md) and [scenario review](../testing/test-scenario-review.md). |
| A scenario fails near a time boundary | Check where the subject reads time and supply a controlled clock through the target's accepted abstraction. Verify time zone and boundary values independently. |
| An operation bypasses an invariant or applies state twice | Trace direct writes and application orchestration back to the aggregate transition. If ES is selected, distinguish replay from new pending events and check `Apply`/`When` ownership. See [aggregate standards](../architecture/ddd-cqrs/aggregate-standards.md). |
| A read exhibits N+1 I/O or unreliable pagination | Inspect actual materialization, selected loading behavior and SQL or provider calls. Verify stable ordering and measure before choosing projection, batching or caching. See [projections](../integration/persistence/projection-standards.md). |

Reproduce the failing condition with the smallest real boundary that exposes
it. Use the linked technical owner to decide the repair. Keep legacy examples
and provider-specific APIs out of unrelated code.

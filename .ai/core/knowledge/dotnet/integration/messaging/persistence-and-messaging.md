# Persistence and messaging integration

Use this reference when the target has selected in-memory event delivery, a
durable messaging path or both. Read the actual ports, provider versions,
composition and delivery contract. EF Core, Dapper, Wolverine, PostgreSQL and
an external broker are conditional choices. The target owns the provider
combination and delivery guarantee.

## Compare the selected paths

| Boundary | In-memory example | Durable outbox example |
| --- | --- | --- |
| Application | Use Case calls project-owned persistence and event publisher ports | The same operation-facing contracts, with any explicitly selected Unit of Work |
| Persistence and outgoing intent | In-memory state and process-local dispatch | The selected completion owner atomically commits the business change and durable outgoing intent |
| Delivery | An in-process dispatcher delivers to registered reactions | A durable dispatcher retries or delivers through the selected transport |
| Evidence | In-process behavior, state and captured events | Local commit and rollback, persisted intent, crash/retry recovery, and actual delivery where claimed |

The Application layer depends on project-owned abstractions. A runtime bus
such as Wolverine's `IMessageBus` belongs in the selected adapter. Keep provider
branches explicit in the [composition root](../../core/host-configuration.md).
When the target adopted the original dual profile, follow its specific
[persistence registrations](../persistence/configuration.md). Use the actual
selected version's startup and durable enrollment APIs. A method named
`UseDurableOutbox` or a successfully built host alone supplies no atomicity
evidence. Verify the selected DbContext, SQL connection or other resource is
enrolled in the intended transaction.

## Durable envelope and completion

Use a versioned envelope with the event identity and metadata required by the
target's accepted contract. Preserve correlation, causation, occurrence time
and audit metadata where specified. [Mapping standards](../persistence/mapper-standards.md)
own event/state conversion and required field coverage. An outbox entity,
database attribute or an in-memory event list cannot by itself prove the
mapping, publication or recovery contract.

Use [transactional messaging](transactional-messaging-standards.md) for the
single physical commit and completion owner, pending-event acknowledgement,
inbox/outbox lifecycle, retry/dead-letter policy and deduplication. Use the
[repository contract](../persistence/repository-standards.md) for persistence
and event acceptance at that boundary. Define compatibility and replay behavior
for the actual published contract. Keep direct vendor calls and transport
retry behavior in their adapters.

## Diagnose a selected path

- A Use Case resolves the vendor bus. Trace the outbound port through the
  composition root and confirm business code only sees the port.
- The in-memory host opens a database connection. Trace the selected
  environment and the first registration that brings in a durable provider.
- State persists but outgoing intent is absent. Verify the actual commit owner
  and transaction enrollment, then exercise rollback and the crash/retry path.
- Rehydration creates new pending events. Inspect the reconstruction path.
  [Reconstruction](../../architecture/ddd-cqrs/building-blocks-reconstruction.md)
  distinguishes historical facts from new events and owns the optional ES contract.
- A local test sees a publication but a broker consumer does not. Check
  subscription, contract identity, retry/dead-letter and actual transport
  evidence. The in-memory path cannot establish any of those durable behaviors.

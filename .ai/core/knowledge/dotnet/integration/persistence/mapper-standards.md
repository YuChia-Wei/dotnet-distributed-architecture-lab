# Mapper Coding Standards (.NET)

Mappers convert supplied objects between representations. Distinguish command-side
Aggregate reconstruction, persistence writes, DTO conversion and optional display
enrichment before choosing failure behavior.

## Pure Object Mapper Structure

A pure object Mapper MUST use a static class and static methods, without instance
state, DI, I/O or orchestration. An Enricher, Assembler or Adapter supplies clock,
user or query inputs. Static syntax proves neither purity, determinism nor complete
round trips. This is the selected Framework policy, distinct from Fowler's
persistence Data Mapper pattern; see
[policy rationale](../../references/policy-rationale.md#pure-object-mapper-versus-work-with-dependencies).

Handle null inputs explicitly. Reuse `JsonSerializerOptions` where appropriate.
The snippets use target-owned types and an exception failure policy; an explicit
failed Result with no usable Aggregate is equally valid. No serializer, error
class or ArchPrecept dependency is prescribed.

## Write-Model Round Trips and Reconstruction

`ToData` / `ToDomain` MUST preserve all state required by the selected invariant,
metadata and event contract. Check fields and behavior explicitly. A DTO projection
needs no invented inverse. Serialization failure of required persistence state
MUST fail the write; do not save defaults that conceal corruption.

The storage contract selects full history, supported snapshot plus tail, or current
state. A pending-event batch is not full committed history. Missing history MUST
NOT trigger an improvised state fallback or manufacture historical event IDs or
timestamps. Validate schema/event versions before returning a usable Aggregate;
unknown versions, malformed required data and missing required state fail.

```csharp
// Selected current-state contract: DefinitionOfDone is required business state.
// Product(RestoredProductState) validates complete restored state without
// recording creation events or running today's creation preconditions.
public static Product ToDomain(ProductData data)
{
    ArgumentNullException.ThrowIfNull(data);
    if (data.SchemaVersion != 1)
        throw new NotSupportedException("Unsupported Product state schema.");
    if (string.IsNullOrWhiteSpace(data.DefinitionOfDoneJson))
        throw new InvalidDataException("Required DefinitionOfDone is missing.");

    // JsonException propagates; JSON null is not successful reconstruction.
    var definition = JsonSerializer.Deserialize<DefinitionOfDone>(
        data.DefinitionOfDoneJson, JsonOptions)
        ?? throw new InvalidDataException("Required DefinitionOfDone is null.");
    var state = new RestoredProductState(
        ProductId.From(data.Id), data.Name, data.CreatorId, definition,
        data.IsDeleted, data.CreatedAt, data.UpdatedAt);
    return new Product(state);
}
```

Validate the required representation before exposing the instance. If construction
or replay partly mutates an object and fails, propagate failure and discard it;
it cannot execute commands or be saved. The Repository/adapter retains record or
stream identity, field and version context without leaking sensitive payloads.
The target data owner owns repair, migration or quarantine. Identity alone does
not prove business completeness.

```csharp
// Incorrect: required state is lost although identity survives.
var product = new Product(partialState);
try { RestoreRequiredDefinition(product, data.DefinitionOfDoneJson); }
catch (JsonException) { /* continue */ }
return product; // Can execute/save a corrupted default: reject this contract.
```

## Creation and Historical Facts

Creation checks today's command preconditions and produces new facts. Rehydration
restores accepted facts without re-running creation, sending notifications,
querying today's exchange rate or recording fresh events. Historical facts use
the selected version/compatibility rules; do not apply today's command precondition
to invalidate previously valid history. This does not permit ignoring unknown
events or missing invariant state. Upcasting, migration, snapshot support and
historical invariant compatibility require target-owner decisions.

```csharp
// Selected ES contract: Product(history) replays a complete ordered stream
// after derived initialization and leaves no new pending events.
public static Product FromHistory(IReadOnlyList<IDomainEvent> history)
{
    ArgumentNullException.ThrowIfNull(history);
    return new Product(history); // Failure escapes; no partial instance returned.
}
// Incorrect: call Create/Rename/CommitSprint/MarkAsDeleted to rebuild history,
// then erase their events. Clearing cannot undo external side effects.
```

### Pending Domain Events After Reconstruction

An Aggregate returned by reconstruction MUST contain no events eligible for
publication or persistence as new business facts. Restore historical/persisted
state through the selected rehydration/replay protocol, not command methods.

- Successful replay restores state without enqueueing history as new pending
  events. Current-state reconstruction has the same no-new-facts obligation.
- Do not require `ClearDomainEvents()` as a generic fallback. Its legality and
  meaning depend on the selected contract. Unknown cleanliness is an unresolved
  contract: fail/stop affected reconstruction until verified; clearing an unknown
  instance does not prove safe reconstruction.
- For ArchPrecept CT-005, successful `LoadFromHistory` leaves pending empty;
  `ClearDomainEvents()` is prohibited. Replay/transition failure poisons the
  instance: discard it. Confirm new events through `MarkChangesAsCommitted`
  only after successful append of the entire pending batch.
- For a package-free/custom contract, verify equivalent replay, failure and
  commit behavior. Use clear/ack only where the selected protocol permits it
  after the relevant durable success, never to conceal replay failure.
- Append failure does not acknowledge pending events. An unknown append outcome
  requires storage-side reconciliation using the selected operation identity or
  idempotency/query protocol before retry or local acknowledgement. Do not blindly
  resend, clear pending or infer durable success from a local method.

## Selected Optional Display Degradation

Only explicitly selected, dispensable display fields that cannot affect invariants
may degrade. Return visible incompleteness and its reason. Do not return a
persistable Aggregate or save the display fallback as business truth.

```csharp
// Selected: Badge is display-only; Id/Name are validated required DTO inputs.
// This DTO never serves as command state. No logger/I/O inside the Mapper.
public static ProductCard ToCard(ProductCardData data)
{
    ArgumentNullException.ThrowIfNull(data);
    ArgumentException.ThrowIfNullOrWhiteSpace(data.Id);
    ArgumentException.ThrowIfNullOrWhiteSpace(data.Name);
    try
    {
        var badge = string.IsNullOrWhiteSpace(data.BadgeJson) ? null
            : JsonSerializer.Deserialize<Badge>(data.BadgeJson, JsonOptions);
        return new(data.Id, data.Name, badge, badge is null,
            badge is null ? "Optional badge unavailable" : null);
    }
    catch (JsonException)
    {
        return new(data.Id, data.Name, null, true, "Invalid optional badge");
    }
}
public sealed record ProductCard(
    string Id, string Name, Badge? Badge, bool IsIncomplete, string? Reason);
```

This is not a general catch/continue policy for complex fields. An unselected
fallback or a price, permission, committed-sprint list or invariant-relevant field
MUST NOT use it. Pure DTO mapping can also fail its required output contract.
Do not catch every exception, cancellation, infrastructure failure or programmer
defect as a missing badge.

## Field and Metadata Coverage

- Preserve required scalar/complex state and metadata in both directions for the
  selected write contract. Null/default collections are valid only where the
  persisted schema explicitly defines that meaning.
- Map `IsDeleted` when `DELETE-SOFT-001` applies; target opt-outs add no synthetic
  field. Restore deletion state through rehydration, not a fresh delete command.
- Preserve stream/event identities, ordering, versions and metadata for the
  selected ES/outbox path. Pending batches, full history, snapshots and state
  records are distinct representations.
- When adding Aggregate state, update schema and conversion together. Restore a
  committed-sprint collection from validated persisted entries in a state
  constructor; do not call `CommitSprint` per entry or default missing required
  JSON to an empty collection.
- Rebuild Value Objects through accepted target contracts. `From`/`ValueOf`
  spellings are illustrative, not required package APIs.

Confirm the actual storage columns or serialized members and required metadata
for each supported version. Under an adopted primitive-only data shape, map
enum and value-object representations explicitly in the pure mapper. If an
adapter stores complex values or collections as JSON, validate schema and
version before restoring required state. EF Core configuration belongs to the
selected persistence adapter. Outbox envelopes follow the selected event and
delivery contract.

## Review Checklist

- [ ] Static pure conversion, explicit inputs/null handling, no hidden I/O.
- [ ] Required state/metadata round trips; serialization errors cannot save defaults.
- [ ] Selected history/state/schema/event-version contract is explicit; missing,
      unsupported or corrupt required data returns no usable Aggregate.
- [ ] Partial instances discarded; diagnosis and data-repair ownership identifiable.
- [ ] Creation, historical replay and external side effects remain distinct.
- [ ] Reconstruction leaves no new publishable events under a verified protocol;
      no generic Clear fallback or durable success inferred from a local method.
- [ ] Optional display fallback explicitly selected and visibly incomplete;
      required DTO data and invariants protected.
- [ ] Deletion, nested state, timestamps and identities preserved without inventing
      history or an inverse DTO conversion.
- [ ] Cases cover required-data failure, unsupported versions, optional display,
      replay failure and unknown append outcomes.

## Related Documents

- [Aggregate standards](../../architecture/ddd-cqrs/aggregate-standards.md)
- [Repository standards](repository-standards.md)
- [Query/projector standards](projection-standards.md)
- [contract cases](../../testing/reconstruction-and-projector-cases.md)
- [Official sources and interpretation](../../references/policy-rationale.md#reconstruction-and-projection-sources)

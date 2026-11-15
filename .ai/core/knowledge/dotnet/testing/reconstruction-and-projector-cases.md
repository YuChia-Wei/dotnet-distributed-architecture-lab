# Reconstruction and projector cases

Use these cases with the [mapper](../integration/persistence/mapper-standards.md) and
[projector](../integration/persistence/projection-standards.md#event-driven-read-model-projector) contracts.
The [domain contract test templates](domain-contract-examples.md)
generate runnable examples for aggregate reconstruction.

## Behavior cases

| Given / when | Required outcome and responsibility |
|---|---|
| Required DefinitionOfDone is absent, JSON null or malformed on a command-side load | Explicit failure with no usable Aggregate; adapter identifies record/field/schema, data owner repairs. Never catch/continue or save defaults. |
| State schema or historical event version is unsupported | Fail visibly; target owner selects compatibility/upcasting/migration. A known identity does not authorize partial success. |
| A display-only badge is explicitly dispensable, and its JSON is malformed | A DTO with `IsIncomplete` and a reason is valid; no Aggregate or business-state write is produced. |
| The same fallback is unselected or applied to price/permission/required state | Reject degradation. DTOs also fail when their own required contract cannot be met. |
| A formerly valid creation event conflicts with today's command precondition | Replay under the selected historical compatibility rule, without rerunning today's command. Unsupported history still fails; do not silently drop it. |
| Replay encounters an unknown event after partially restoring state | Failure escapes and instance is discarded. No command/save/clear-based recovery of the partial instance. |
| A new command versus replay of an old fact | Only the new command records a new pending fact; replay sends no email, payment or other external effect. |
| Duplicate projector delivery after read commit but failed ack | Deduplicate the committed event and retry acknowledgement under the selected transaction/retention policy. |
| Read write/commit fails | Roll back and leave checkpoint/ack incomplete; retry/park under the selected policy. |
| Separately stored checkpoint/ack fails or is unknown | Reconcile it and replay idempotently; do not advance past an unprocessed sequence gap or claim exactly-once. |
| Query reader writes, or projector changes command state/publishes externally | Reject under those roles; owned read-store projection grants neither capability. |

## Optional ArchPrecept API

ArchPrecept.Contracts.Domain and Domain.EventSourcing `0.0.3-preview` are an
optional implementation. The [fixed CT-005 contract](https://github.com/YuChia-Wei/ArchPrecept/blob/fdc1f9ff3934c769047f797803abc8614290e889/docs/product/event-sourcing-contract.md) defines poisoning and commit behavior.
The package-free ES snippet instead requires callers to discard failed instances.
Target adoption, historical compatibility and storage transactions remain explicit decisions.

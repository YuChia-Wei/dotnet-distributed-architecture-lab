# Optional Domain Source Includes

This folder contains the minimal source-includable Domain contracts approved for
the dotnet-backend profile. It is not a NuGet package, product fixture, or
complete BuildingBlocks implementation.

The default contract is interface-first:

- `IDomainEntity<TId>`;
- `IAggregateRoot<TId>`;
- `IDomainEvent`.

`EsAggregateRoot<TId>` is the only supplied optional base class. Its mechanical
replay, pending-event, transition-dispatch, and committed-version behavior is
specified independently in
[the BuildingBlocks reconstruction contract](../../../../../../.dev/standards/BUILDING-BLOCKS-RECONSTRUCTION-CONTRACT.md).

If a target copies these files, the copies become target-owned. Rename the
provisional `BuildingBlocks.Domain` namespace as needed, record local changes,
and use `ai-context-upgrader` three-way comparison for later framework upgrades.
Targets may reimplement the documented behavior instead of copying this source.

The machine-readable evidence tier and verification commands are declared in
[`../evidence-manifest.yaml`](../evidence-manifest.yaml).

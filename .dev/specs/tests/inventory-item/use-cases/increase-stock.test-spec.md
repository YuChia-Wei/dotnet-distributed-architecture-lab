# IncreaseStock Test Spec

## Scope

Application and integration-aware verification for `IncreaseStock`.

## Implementation Status

- Status: `implemented-broker-free`; PostgreSQL atomicity remains an opt-in external gate.
- Anchor: `tests/InventoryControl.Tests/InventoryStockUseCaseTests.cs`

## Related Production Spec

- `.dev/specs/domains/inventory-item/usecase/increase-stock.json`

## Scenario List

- Happy path: existing inventory item stock increases successfully
- Failure path: target inventory item does not exist
- Integration path: successful increase publishes stock-increased integration event

## Given-When-Then

### Scenario 1: increase stock succeeds

- Given:
  - an inventory item exists for the target product
- When:
  - `IIncreaseStockUseCase.ExecuteAsync` is invoked with `IncreaseStockInput` containing a positive quantity
- Then:
  - current stock is increased
  - `IInventoryStockOutbox` receives the mutated aggregate and expected prior stock
  - a `ProductStockIncreasedIntegrationEvent` plus stable ProductId partition key is staged atomically with persistence

### Scenario 2: inventory item does not exist

- Given:
  - no inventory item exists for the target product id
- When:
  - `IIncreaseStockUseCase.ExecuteAsync` is invoked with `IncreaseStockInput`
- Then:
  - the result indicates inventory-item-not-found semantics
  - no stock increase is committed
  - no stock-increased integration event is staged

## Assertions

- `Result<IncreaseStockOutput>` success or failure content
- stock mutation or non-mutation
- outbox save-and-stage behavior
- event schema, non-empty message ID, and ProductId partition key

## Test Level

- Primary: `application`
- Secondary: `contract`

## Notes / Deferred Cases

- Quantity validation edge cases should be expanded once the exact command validation contract is documented.

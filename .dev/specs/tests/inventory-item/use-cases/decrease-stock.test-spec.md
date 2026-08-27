# DecreaseStock Test Spec

## Scope

Aggregate and application verification for `DecreaseStock`.

## Implementation Status

- Status: `implemented-broker-free`; PostgreSQL atomicity remains an opt-in external gate.
- Anchor: `tests/InventoryControl.Tests/InventoryStockUseCaseTests.cs`

## Related Production Spec

- `.dev/specs/domains/inventory-item/usecase/decrease-stock.json`

## Scenario List

- Happy path: enough stock exists and stock decreases successfully
- Failure path: requested quantity exceeds current stock
- Failure path: inventory item does not exist
- Integration path: successful decrease emits stock-decreased integration event

## Given-When-Then

### Scenario 1: decrease succeeds

- Given:
  - an inventory item exists for the target product
  - current stock is greater than or equal to the requested quantity
- When:
  - `IDecreaseStockUseCase.ExecuteAsync` is invoked with `DecreaseStockInput`
- Then:
  - the aggregate stock is reduced
  - `IInventoryStockOutbox` receives the mutated aggregate and expected prior stock
  - a `ProductStockDecreasedIntegrationEvent` plus stable ProductId partition key is staged atomically with persistence

### Scenario 2: insufficient stock

- Given:
  - an inventory item exists
  - current stock is lower than the requested quantity
- When:
  - `IDecreaseStockUseCase.ExecuteAsync` is invoked with `DecreaseStockInput`
- Then:
  - the result indicates failure
  - the aggregate is not committed with a reduced stock
  - no stock-decreased integration event is staged

## Assertions

- `Result<DecreaseStockOutput>` success or failure content
- stock mutation or non-mutation
- outbox save-and-stage behavior
- event schema, non-empty message ID, and ProductId partition key

## Test Level

- Primary: `application`
- Secondary: `unit`

## Notes / Deferred Cases

- Duplicate consumption and replay/idempotency scenarios should later be expanded once Stage 5 runtime docs exist.

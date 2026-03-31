# DecreaseStock Test Spec

## Scope

Aggregate and application verification for `DecreaseStock`.

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
  - `DecreaseStockCommand` is handled
- Then:
  - the aggregate stock is reduced
  - persistence is performed
  - a `ProductStockDecreasedIntegrationEvent` is published

### Scenario 2: insufficient stock

- Given:
  - an inventory item exists
  - current stock is lower than the requested quantity
- When:
  - `DecreaseStockCommand` is handled
- Then:
  - the result indicates failure
  - the aggregate is not persisted with a reduced stock
  - no stock-decreased integration event is published

## Assertions

- result DTO content
- stock mutation or non-mutation
- repository save behavior
- integration event publication behavior

## Test Level

- Primary: `application`
- Secondary: `unit`

## Notes / Deferred Cases

- Duplicate consumption and replay/idempotency scenarios should later be expanded once Stage 5 runtime docs exist.

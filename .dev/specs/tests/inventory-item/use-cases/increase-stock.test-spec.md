# IncreaseStock Test Spec

## Scope

Application and integration-aware verification for `IncreaseStock`.

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
  - `IncreaseStockCommand` is handled with a positive quantity
- Then:
  - current stock is increased
  - persistence is performed
  - a `ProductStockIncreasedIntegrationEvent` is published

### Scenario 2: inventory item does not exist

- Given:
  - no inventory item exists for the target product id
- When:
  - `IncreaseStockCommand` is handled
- Then:
  - the result indicates inventory-item-not-found semantics
  - no stock increase is persisted
  - no stock-increased integration event is published

## Assertions

- result DTO content
- stock mutation or non-mutation
- repository save behavior
- integration event publication behavior

## Test Level

- Primary: `application`
- Secondary: `contract`

## Notes / Deferred Cases

- Quantity validation edge cases should be expanded once the exact command validation contract is documented.

# Inventory Stock Persistence And Publication Test Spec

## Scope

Integration-focused verification for inventory persistence and outbound stock integration events.

## Related Production Spec

- `.dev/specs/domains/inventory-item/usecase/decrease-stock.json`
- `.dev/specs/domains/inventory-item/usecase/increase-stock.json`
- `.dev/specs/domains/inventory-item/usecase/restock.json`

## Scenario List

- Happy path: stock decrease persists and publishes `ProductStockDecreasedIntegrationEvent`
- Happy path: stock increase persists and publishes `ProductStockIncreasedIntegrationEvent`
- Happy path: restock persists and publishes `ProductStockReturnedIntegrationEvent`
- Failure path: not-found or insufficient-stock outcomes do not publish success events

## Given-When-Then

### Scenario 1: decrease stock with persistence and publication

- Given:
  - an inventory item exists and has sufficient stock
- When:
  - `DecreaseStockCommand` is handled
- Then:
  - the updated stock is persisted
  - a `ProductStockDecreasedIntegrationEvent` is published

### Scenario 2: increase stock with persistence and publication

- Given:
  - an inventory item exists
- When:
  - `IncreaseStockCommand` is handled
- Then:
  - the updated stock is persisted
  - a `ProductStockIncreasedIntegrationEvent` is published

### Scenario 3: restock with persistence and publication

- Given:
  - an inventory item exists
- When:
  - `RestockCommand` is handled
- Then:
  - the updated stock is persisted
  - a `ProductStockReturnedIntegrationEvent` is published

### Scenario 4: suppress success publication on business failure

- Given:
  - the inventory item is missing, or stock is insufficient for decrease
- When:
  - the corresponding command is handled
- Then:
  - no success integration event is published
  - no invalid stock mutation is persisted

## Assertions

- repository load/save behavior
- persisted stock values
- integration event publication behavior
- suppression of success publication on failed operations

## Test Level

- Primary: `integration`
- Secondary: `contract`

## Notes / Deferred Cases

- Replay, duplicate-consumption, and dead-letter recovery concerns belong to Stage 5 runtime documentation.

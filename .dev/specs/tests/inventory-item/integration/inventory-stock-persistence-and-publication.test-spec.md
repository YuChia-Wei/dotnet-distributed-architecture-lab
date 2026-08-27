# Inventory Stock Persistence And Publication Test Spec

## Scope

Integration-focused verification for inventory persistence and outbound stock integration events.

## Implementation Status

- Status: `partially-implemented`
- Broker-free Application/outbox contract anchors exist in `tests/InventoryControl.Tests/InventoryStockUseCaseTests.cs`. Real PostgreSQL atomic-commit and expected-stock concurrency anchors exist in `tests/InventoryControl.Tests/PostgresInventoryStockOutboxTests.cs`; they are opt-in external tests, and a skipped result is non-passing evidence.

## Related Production Spec

- `.dev/specs/domains/inventory-item/usecase/decrease-stock.json`
- `.dev/specs/domains/inventory-item/usecase/increase-stock.json`
- `.dev/specs/domains/inventory-item/usecase/restock.json`

## Scenario List

- Happy path: stock decrease and `ProductStockDecreasedIntegrationEvent` outbox row commit together
- Happy path: stock increase and `ProductStockIncreasedIntegrationEvent` outbox row commit together
- Happy path: restock and `ProductStockReturnedIntegrationEvent` outbox row commit together
- Failure path: not-found or insufficient-stock outcomes do not stage success events
- Concurrency path: expected-stock mismatch rolls back and produces no outbox row

## Given-When-Then

### Scenario 1: decrease stock with persistence and publication

- Given:
  - an inventory item exists and has sufficient stock
- When:
  - `IDecreaseStockUseCase.ExecuteAsync` is invoked with `DecreaseStockInput`
- Then:
  - the updated stock and one `ProductStockDecreasedIntegrationEvent` outbox row are committed atomically

### Scenario 2: increase stock with persistence and publication

- Given:
  - an inventory item exists
- When:
  - `IIncreaseStockUseCase.ExecuteAsync` is invoked with `IncreaseStockInput`
- Then:
  - the updated stock and one `ProductStockIncreasedIntegrationEvent` outbox row are committed atomically

### Scenario 3: restock with persistence and publication

- Given:
  - an inventory item exists
- When:
  - `IRestockUseCase.ExecuteAsync` is invoked with `RestockInput`
- Then:
  - the updated stock and one `ProductStockReturnedIntegrationEvent` outbox row are committed atomically

### Scenario 4: suppress success publication on business failure

- Given:
  - the inventory item is missing, or stock is insufficient for decrease
- When:
  - the corresponding command is handled
- Then:
  - no success integration event is staged
  - no invalid stock mutation is persisted

## Assertions

- repository load and outbox save-and-stage behavior
- persisted stock values
- integration-event staging and relay behavior
- suppression of success publication on failed operations

## Test Level

- Primary: `integration`
- Secondary: `contract`

## Notes / Deferred Cases

- Replay, duplicate-consumption, and dead-letter recovery concerns belong to Stage 5 runtime documentation.

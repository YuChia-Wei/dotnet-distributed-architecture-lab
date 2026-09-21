# Initialize and Query Stock Test Spec

## Inputs Used

- `INV-001`, `INV-002`, `INV-003`, `INV-008`, and `API-003` in `.dev/requirement/reconstructable-system-baseline.md`
- `.dev/specs/domains/inventory-item/usecase/init-product-stock.json`
- `.dev/specs/domains/inventory-item/usecase/get-available-quantity.json`

## Implementation Status

- Status: `implemented-partial`
- `tests/InventoryControl.Tests/InventoryEfPersistenceTests.cs` covers repository persistence and the available-quantity read projection. The 2026-09-21 commerce run at `edd18d70a94da99e0548de986227655ec102a145` passed Inventory seed/read; see [dated execution evidence](../../../reconstruction/coverage-matrix.md#observed-execution--2026-09-21). Direct initialize/query use-case validation and not-found assertions remain gaps.

## Scenario Set

### Scenario 1: initialize valid stock

- Test level: `application`
- Given: no inventory row exists and initial stock is non-negative.
- When: `IInitProductStockUseCase.ExecuteAsync` runs.
- Then: one item is persisted and the result contains its stock value. No integration event is staged because no producer-owned initialization event contract exists.

### Scenario 2: reject invalid initial stock

- Test level: `aggregate`
- Given: initial stock is negative.
- When: initialization is attempted.
- Then: the required quality-uplift contract rejects the input; no persistence or publication occurs.

### Scenario 3: query available quantity

- Test level: `application`
- Given: an inventory row exists for the product.
- When: `IGetInventoryItemAvailableQuantityUseCase.ExecuteAsync` runs.
- Then: the result succeeds and returns the exact available quantity.

### Scenario 4: query a missing item

- Test level: `application`
- Given: no row exists for the product.
- When: the query use case runs.
- Then: the result is failure/not-found and does not return a fabricated zero balance.

## Assertion Notes

- Verify persistence and the absence of an invented initialization integration event; initialization has no publish-order contract.
- Negative initialization is a `quality-uplift` scenario and should fail against current source until implemented.

## Recommended Test Spec Path

`.dev/specs/tests/inventory-item/use-cases/initialize-and-query-stock.test-spec.md`

## Implementation and Execution Handoff

Concrete Inventory tests require a separately authorized implementation slice.

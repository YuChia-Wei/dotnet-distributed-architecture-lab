# InventoryItem Aggregate Test Spec

## Scope

Aggregate-focused verification for `InventoryItem` stock mutation rules and business failures.

## Related Production Spec

- `.dev/specs/domains/inventory-item/entity/inventory-item-spec.md`

## Scenario List

- Happy path: increase stock mutates current stock and records `StockIncreased`
- Happy path: decrease stock mutates current stock and records `StockDecreased`
- Happy path: restock returned quantity mutates current stock and records `StockReturned`
- Failure path: insufficient stock rejects decrease without invalid mutation

## Given-When-Then

### Scenario 1: increase stock

- Given:
  - an existing inventory item with current stock
- When:
  - `InventoryItem.IncreaseStock` is invoked with a positive quantity
- Then:
  - current stock increases
  - a `StockIncreased` domain event is recorded

### Scenario 2: decrease stock with enough availability

- Given:
  - current stock is greater than or equal to the requested quantity
- When:
  - `InventoryItem.DecreaseStock` is invoked
- Then:
  - current stock decreases
  - a `StockDecreased` domain event is recorded

### Scenario 3: restock returned quantity

- Given:
  - an existing inventory item with current stock
- When:
  - `InventoryItem.Restock` is invoked with a positive quantity
- Then:
  - current stock increases
  - a `StockReturned` domain event is recorded

### Scenario 4: reject insufficient stock decrease

- Given:
  - requested quantity exceeds available stock
- When:
  - `InventoryItem.DecreaseStock` is invoked
- Then:
  - the operation returns a business failure result
  - current stock does not decrease
  - no stock-decreased success event is recorded

## Assertions

- stock mutation and non-mutation behavior
- domain result semantics for expected failures
- domain event recording behavior

## Test Level

- Primary: `unit`
- Secondary: `application`

## Notes / Deferred Cases

- Negative quantity validation should be expanded once command and aggregate validation boundaries are documented consistently.

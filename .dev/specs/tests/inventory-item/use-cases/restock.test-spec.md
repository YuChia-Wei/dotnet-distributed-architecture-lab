# Restock Test Spec

## Scope

Application and integration-aware verification for `Restock`.

## Related Production Spec

- `.dev/specs/domains/inventory-item/usecase/restock.json`

## Scenario List

- Happy path: returned stock is added back to inventory
- Failure path: target inventory item does not exist
- Integration path: successful restock publishes stock-returned integration event

## Given-When-Then

### Scenario 1: restock succeeds

- Given:
  - an inventory item exists for the target product
- When:
  - `RestockCommand` is handled with a positive quantity
- Then:
  - current stock is increased by the returned quantity
  - persistence is performed
  - a `ProductStockReturnedIntegrationEvent` is published

### Scenario 2: inventory item does not exist

- Given:
  - no inventory item exists for the target product id
- When:
  - `RestockCommand` is handled
- Then:
  - the result indicates inventory-item-not-found semantics
  - no stock return is persisted
  - no stock-returned integration event is published

## Assertions

- result DTO content
- stock mutation or non-mutation
- repository save behavior
- integration event publication behavior

## Test Level

- Primary: `application`
- Secondary: `contract`

## Notes / Deferred Cases

- The handler naming typo noted in the production spec should remain visible until code and docs are normalized together in a later workflow.

# PlaceOrder Test Spec

## Scope

Application-level and integration-aware verification for `PlaceOrder`.

## Related Production Spec

- `.dev/specs/domains/order/usecase/place-order.json`

## Scenario List

- Happy path: inventory reservation succeeds and order is placed
- Failure path: inventory reservation fails and order placement returns failure
- Integration path: successful order placement emits `OrderPlaced` integration event

## Given-When-Then

### Scenario 1: successful order placement

- Given:
  - an inventory reservation request for the target product will succeed
  - the order repository accepts persistence
- When:
  - `PlaceOrderCommand` is handled with valid order date, amount, product id, product name, and quantity
- Then:
  - a new order is persisted
  - the result is successful and returns an order id
  - an `OrderPlaced` integration event is published

### Scenario 2: inventory not enough

- Given:
  - the inventory gateway returns `Result = false`
- When:
  - `PlaceOrderCommand` is handled
- Then:
  - the result is a failure
  - no order is persisted
  - no `OrderPlaced` integration event is published

## Assertions

- success/failure result semantics
- repository save behavior
- inventory gateway invocation
- integration event publication behavior

## Test Level

- Primary: `application`
- Secondary: `contract`

## Notes / Deferred Cases

- Duplicate delivery and MQ retry behavior belong to Stage 5 runtime docs and later test scenarios.

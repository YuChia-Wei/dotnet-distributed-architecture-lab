# DeliverOrder Test Spec

## Scope

Application and integration-aware verification for `DeliverOrder`.

## Related Production Spec

- `.dev/specs/domains/order/usecase/deliver-order.json`

## Scenario List

- Happy path: existing order is marked as delivered
- Failure path: target order does not exist
- Integration path: successful delivery publishes `OrderDelivered`

## Given-When-Then

### Scenario 1: deliver succeeds for an existing order

- Given:
  - an existing order is loaded by id
- When:
  - `DeliverOrderCommand` is handled
- Then:
  - the order status becomes `Delivered`
  - persistence is performed
  - an `OrderDelivered` integration event is published

### Scenario 2: order does not exist

- Given:
  - no order exists for the requested id
- When:
  - `DeliverOrderCommand` is handled
- Then:
  - the operation fails with `KeyNotFoundException` or equivalent not-found semantics
  - no status change is persisted
  - no `OrderDelivered` integration event is published

## Assertions

- repository load and save behavior
- order status transition
- integration event publication behavior
- not-found failure semantics

## Test Level

- Primary: `application`
- Secondary: `contract`

## Notes / Deferred Cases

- Preconditions around shipping-before-delivery should be revisited once aggregate-level transition rules are documented separately.

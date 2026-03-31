# CancelOrder Test Spec

## Scope

Application and integration-aware verification for `CancelOrder`.

## Related Production Spec

- `.dev/specs/domains/order/usecase/cancel-order.json`

## Scenario List

- Happy path: existing order is marked as cancelled
- Failure path: target order does not exist
- Integration path: successful cancellation publishes `OrderCancelled`

## Given-When-Then

### Scenario 1: cancel succeeds for an existing order

- Given:
  - an existing order is loaded by id
- When:
  - `CancelOrderCommand` is handled
- Then:
  - the order status becomes `Cancelled`
  - persistence is performed
  - an `OrderCancelled` integration event is published

### Scenario 2: order does not exist

- Given:
  - no order exists for the requested id
- When:
  - `CancelOrderCommand` is handled
- Then:
  - the operation fails with `KeyNotFoundException` or equivalent not-found semantics
  - no status change is persisted
  - no `OrderCancelled` integration event is published

## Assertions

- repository load and save behavior
- order status transition
- integration event publication behavior
- not-found failure semantics

## Test Level

- Primary: `application`
- Secondary: `contract`

## Notes / Deferred Cases

- Compensation behavior against downstream consumers should be expanded later in cross-domain runtime scenarios.

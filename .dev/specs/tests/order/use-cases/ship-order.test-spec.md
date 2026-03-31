# ShipOrder Test Spec

## Scope

Application and integration-aware verification for `ShipOrder`.

## Related Production Spec

- `.dev/specs/domains/order/usecase/ship-order.json`

## Scenario List

- Happy path: existing order is marked as shipped
- Failure path: target order does not exist
- Integration path: successful shipment publishes `OrderShipped`

## Given-When-Then

### Scenario 1: ship succeeds for an existing order

- Given:
  - an existing order is loaded by id
- When:
  - `ShipOrderCommand` is handled
- Then:
  - the order status becomes `Shipped`
  - persistence is performed
  - an `OrderShipped` integration event is published

### Scenario 2: order does not exist

- Given:
  - no order exists for the requested id
- When:
  - `ShipOrderCommand` is handled
- Then:
  - the operation fails with `KeyNotFoundException` or equivalent not-found semantics
  - no status change is persisted
  - no `OrderShipped` integration event is published

## Assertions

- repository load and save behavior
- order status transition
- integration event publication behavior
- not-found failure semantics

## Test Level

- Primary: `application`
- Secondary: `contract`

## Notes / Deferred Cases

- Delivery ordering and duplicate publication concerns belong to Stage 5 runtime documentation and later integration specs.

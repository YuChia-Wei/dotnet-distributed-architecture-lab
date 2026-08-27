# PlaceOrder Test Spec

## Scope

Application-level and integration-aware verification for `PlaceOrder`.

## Implementation Status

- Status: `implemented-partial`
- `tests/SaleOrders.Tests/PlaceOrderTests.cs` directly verifies successful reservation plus atomic commit and the reservation-failure no-commit branch.
- Gateway exception/timeout and source-transaction failure branches remain planned.

## Related Production Spec

- `.dev/specs/domains/order/usecase/place-order.json`

## Scenario List

- Happy path: inventory reservation succeeds and order is placed
- Failure path: inventory reservation fails and order placement returns failure
- Integration path: successful order placement commits `OrderPlaced` to the source outbox
- Failure path: source commit fails and neither order state nor publishable outbox state becomes externally successful

## Given-When-Then

### Scenario 1: successful order placement

- Given:
  - an inventory reservation request for the target product will succeed
  - the order repository accepts persistence
- When:
  - `IPlaceOrderUseCase.ExecuteAsync` is invoked with a valid `PlaceOrderInput`
- Then:
  - a new order is persisted
  - the result is successful and returns an order id
  - an `OrderPlaced` integration event is committed to the source outbox

### Scenario 2: inventory not enough

- Given:
  - the inventory gateway returns `Result = false`
- When:
  - `IPlaceOrderUseCase.ExecuteAsync` is invoked with `PlaceOrderInput`
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

- Reservation replay and MQ delivery identity are specified separately in `.dev/specs/tests/cross-domain/order-inventory-reservation.test-spec.md`.

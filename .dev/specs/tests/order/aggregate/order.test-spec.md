# Order Aggregate Test Spec

## Scope

Aggregate-focused verification for `Order` lifecycle transitions and domain events.

## Related Production Spec

- `.dev/specs/domains/order/entity/order-spec.md`

## Scenario List

- Happy path: placed order starts in `Placed` status with `OrderPlacedDomainEvent`
- Happy path: ship transitions status to `Shipped`
- Happy path: deliver transitions status to `Delivered`
- Happy path: cancel transitions status to `Cancelled`

## Given-When-Then

### Scenario 1: order starts in placed status

- Given:
  - valid product id, product name, quantity, order date, and total amount
- When:
  - an `Order` aggregate is created
- Then:
  - the initial status is `Placed`
  - an `OrderPlacedDomainEvent` is recorded

### Scenario 2: ship an existing order

- Given:
  - an existing order in a shippable state
- When:
  - `Order.Ship` is invoked
- Then:
  - status becomes `Shipped`
  - an `OrderShippedDomainEvent` is recorded

### Scenario 3: deliver an existing order

- Given:
  - an existing order in a deliverable state
- When:
  - `Order.Deliver` is invoked
- Then:
  - status becomes `Delivered`
  - an `OrderDeliveredDomainEvent` is recorded

### Scenario 4: cancel an existing order

- Given:
  - an existing order in a cancellable state
- When:
  - `Order.Cancel` is invoked
- Then:
  - status becomes `Cancelled`
  - an `OrderCancelledDomainEvent` is recorded

## Assertions

- status transitions
- event-sourced aggregate event recording
- aggregate field retention across lifecycle methods

## Test Level

- Primary: `unit`
- Secondary: `application`

## Notes / Deferred Cases

- Illegal transition rules should be expanded once the aggregate’s exact transition guards are documented as production truth.

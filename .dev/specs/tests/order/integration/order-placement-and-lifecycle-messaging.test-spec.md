# Order Placement And Lifecycle Messaging Test Spec

## Scope

Integration-focused verification for Orders collaboration with Inventory and outbound order lifecycle events.

## Related Production Spec

- `.dev/specs/domains/order/usecase/place-order.json`
- `.dev/specs/domains/order/usecase/ship-order.json`
- `.dev/specs/domains/order/usecase/deliver-order.json`
- `.dev/specs/domains/order/usecase/cancel-order.json`

## Scenario List

- Happy path: place order succeeds only after inventory reservation succeeds
- Failure path: failed inventory reservation prevents order persistence and event publication
- Happy path: ship, deliver, and cancel flows publish their corresponding integration events after persistence

## Given-When-Then

### Scenario 1: place order after successful inventory reservation

- Given:
  - the inventory collaboration contract returns success
  - the order repository is available
- When:
  - `PlaceOrderCommand` is handled
- Then:
  - the order is persisted
  - an `OrderPlaced` integration event is published

### Scenario 2: block order placement when inventory reservation fails

- Given:
  - the inventory collaboration contract returns failure
- When:
  - `PlaceOrderCommand` is handled
- Then:
  - no order is persisted
  - no `OrderPlaced` integration event is published

### Scenario 3: publish lifecycle integration events after state changes

- Given:
  - an existing order is loaded successfully
- When:
  - `ShipOrderCommand`, `DeliverOrderCommand`, or `CancelOrderCommand` is handled
- Then:
  - the new order state is persisted
  - the matching integration event is published after persistence

## Assertions

- inventory gateway contract invocation
- repository persistence ordering
- integration event publication behavior
- absence of publish on failed reservation

## Test Level

- Primary: `integration`
- Secondary: `contract`

## Notes / Deferred Cases

- Retry, duplicate publication, and eventual consistency timing should move into Stage 5 runtime documentation and later cross-domain specs.

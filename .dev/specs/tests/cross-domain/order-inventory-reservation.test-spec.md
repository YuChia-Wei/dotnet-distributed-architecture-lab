# Order–Inventory Reservation Test Spec

## Inputs Used

- `SYS-004`, `ORD-005`, `INV-005`, `INT-001` through `INT-005` in `.dev/requirement/reconstructable-system-baseline.md`
- `.dev/problem-frames/orders/cbf/place-order/`
- `.dev/problem-frames/inventory/cbf/reserve-inventory/`
- `.dev/specs/reconstruction/message-contracts.json`

## Implementation Status

- Status: `implemented-partial`
- Each side has focused executable evidence; a broker-backed round trip across both hosts remains planned.

## Scenario Set

### Scenario 1: place after reservation success

- Test level: `contract`
- Given: Orders sends `ReserveInventoryRequestContract` with a stable operation id and Inventory has sufficient stock.
- When: Inventory returns success.
- Then: Inventory decrements once; Orders atomically commits its event stream and `OrderPlaced`; both sides preserve correlation-relevant identities.

### Scenario 2: block placement after reservation failure

- Test level: `contract`
- Given: Inventory returns item-not-found or insufficient-stock.
- When: Orders receives the response.
- Then: placement returns failure; no order stream or source-outbox row is committed.

### Scenario 3: duplicate request delivery

- Test level: `integration`
- Given: the broker redelivers the same operation id, product id, and quantity.
- When: Inventory handles both deliveries.
- Then: stock decreases once; the durable outcome is replayed; response and event delivery identity remain stable.

### Scenario 4: timeout is not business rejection

- Test level: `integration`
- Given: the reservation response is not available within the configured transport window.
- When: the Orders gateway awaits collaboration.
- Then: the current exception propagates and no order commit occurs; the event is not misreported as insufficient stock.

### Scenario 5: transport profile parity

- Test level: `integration`
- Given: Kafka and RabbitMQ profiles are configured independently.
- When: the same contract round trip runs under each profile.
- Then: routing, request/response shape, retry identity, and business result are equivalent; infrastructure-specific metadata may differ.

## Assertion Notes

- Verify there is no direct HTTP call between bounded contexts.
- Scenario 5 needs trusted RabbitMQ runtime evidence; configuration presence alone is not a pass.

## Recommended Test Spec Path

`.dev/specs/tests/cross-domain/order-inventory-reservation.test-spec.md`

## Implementation and Execution Handoff

The workflow does not authorize broker-backed test implementation or execution.

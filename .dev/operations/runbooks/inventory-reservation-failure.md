# Inventory Reservation Failure Runbook

## Trigger

Use this runbook when order placement is failing because inventory reservation does not succeed, or when maintainers observe that `PlaceOrder` requests are returning failure even though the order payload appears valid.

Do not use this runbook for:

- product validation failures
- order lifecycle events after an order has already been placed
- generic API downtime without evidence of reservation-path involvement

## Scope

This runbook covers the request/reply path:

- `Orders` sends `ReserveInventoryRequestContract`
- `Inventory` handles the request through `ReserveInventoryRequestContractHandler`
- `Inventory` invokes `DecreaseStockCommand`
- `Inventory` returns `ReserveInventoryResponseContract`
- `Orders` decides whether to persist and publish `OrderPlaced`

## Symptoms

- `PlaceOrder` returns failure unexpectedly
- no `OrderPlaced` integration event is published
- inventory request messages accumulate or time out
- reply path appears delayed or missing
- stock was expected to be available, but reservation still failed

## Immediate Checks

1. Confirm whether the failure is a business failure or a transport/runtime failure.
2. Check whether `ReserveInventoryResponseContract.Result` is `false` versus missing/timeout behavior.
3. Check the active broker mode from `QUEUE_SERVICE`.
4. Check whether the relevant runtime endpoints are up:
   - `SaleOrders.WebApi`
   - `InventoryControl.WebApi`
5. Check the broker channels involved:
   - `inventory.requests`
   - `orders.outbound.replies`

## Diagnosis Steps

1. Check `Orders` logs around `PlaceOrderCommand` execution.
   - If reservation response is `Result = false`, move to inventory business checks.
   - If reply is missing or times out, move to MQ routing and consumer checks.
2. Check `Inventory` logs around `ReserveInventoryRequestContractHandler`.
   - Confirm the request reached the handler.
   - Confirm `DecreaseStockCommand` executed.
3. Check the inventory aggregate state for the requested `ProductId`.
   - If no inventory item exists, expect `InventoryItemNotFound`.
   - If stock is insufficient, expect a business failure result.
4. Check whether the active broker topology matches runtime configuration.
   - Kafka mode should involve `inventory.requests` and `orders.outbound.replies`.
   - RabbitMQ mode should use the logical queue names configured in Wolverine.
5. Check for inbox/outbox backlog or stuck consumers if request reached the broker but not the handler.

## Recovery Actions

- If the failure is a valid business rejection:
  - do not force order placement
  - correct stock first, then retry the business operation
- If the failure is due to missing inventory item:
  - create or initialize stock through the proper inventory workflow before retry
- If the failure is due to broker routing or consumer outage:
  - restore the affected runtime or broker path first
  - only retry business messages after confirming request/reply flow is healthy
- If duplicate retries may have occurred:
  - inspect stock and order state before replaying any message manually

## Verification

- a fresh `PlaceOrder` attempt succeeds for a product with sufficient stock
- `ReserveInventoryRequestContract` is handled successfully
- `ReserveInventoryResponseContract.Result` returns `true`
- order persistence completes
- `OrderPlaced` is published only after successful reservation

## Escalation / Follow-up

- If repeated failures are caused by unclear routing, create or update `mq-topology.md`.
- If repeated failures are caused by consumer ambiguity or duplicate handling risk, create a follow-up Stage 5 task for replay/idempotency documentation.
- If the reply listener misconfiguration in `SaleOrders.WebApi` is confirmed to be causing production risk, open a dedicated code refactor workflow rather than “fixing” it only in docs.

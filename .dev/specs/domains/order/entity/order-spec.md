# Order Aggregate Spec

## Aggregate
- Name: `Order`
- Bounded Context: `Orders`
- Domain Namespace: `SaleOrders.Domains`

## Description

`Order` represents a customer purchase request and its lifecycle within the Orders bounded context.

## Attributes

- `Id: Guid`
- `ProductId: Guid`
- `ProductName: string`
- `Quantity: int`
- `OrderDate: DateTime`
- `TotalAmount: decimal`
- `Status: OrderStatus`

## State Model

- `Placed`
- `Shipped`
- `Delivered`
- `Cancelled`

## Behaviors

- Place order
- Ship order with a non-blank reason
- Deliver order with a non-blank reason
- Cancel order with a non-blank reason

## Transition Rules

- A transition to any different `Shipped`, `Delivered`, or `Cancelled` status is allowed when a non-blank reason is supplied.
- The reason is recorded in the matching domain event.
- A request to transition to the current status is a no-op and records no new event.
- Missing or whitespace-only reasons are rejected without changing state.

## Domain Events

- `OrderPlacedDomainEvent`
- `OrderShippedDomainEvent`
- `OrderDeliveredDomainEvent`
- `OrderCancelledDomainEvent`

## Notes

- The aggregate is event-sourced in the current implementation.
- Replayed events establish state and version but are not pending events.
- After a successful append, the committed version is advanced and committed pending events are cleared.
- Order placement in the application layer also requires successful inventory reservation before persistence and integration event publication.

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
- Ship order
- Deliver order
- Cancel order

## Domain Events

- `OrderPlacedDomainEvent`
- `OrderShippedDomainEvent`
- `OrderDeliveredDomainEvent`
- `OrderCancelledDomainEvent`

## Notes

- The aggregate is event-sourced in the current implementation.
- Order placement in the application layer also requires successful inventory reservation before persistence and integration event publication.

# Data Model

## Order Entity

The `Order` entity in `SaleOrders.Domains` will be updated with the following:

- A `Status` property of type `OrderStatus` (enum).
- A `Cancel()` method that sets the `Status` to `Cancelled` and raises an `OrderCancelled` domain event.

### OrderStatus Enum

```csharp
public enum OrderStatus
{
    Placed,
    Shipped,
    Cancelled
}
```

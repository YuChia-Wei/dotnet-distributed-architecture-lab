# Research: Retrieving Cancelled Order Details

## Topic: How to retrieve product details for a cancelled order.

### Finding
The initial feature specification assumed that the `OrderCancelled` integration event would contain the list of products and their quantities. However, analysis of the existing contract in `src/BC-Contracts/Lab.MessageSchemas.Orders/IntegrationEvents/OrderCancelled.cs` reveals it only contains the `OrderId`.

```csharp
public record OrderCancelled : IIntegrationEvent
{
    public Guid OrderId { get; }
    // ... other metadata
}
```

This means the `Product.Consumer` does not have enough information to fulfill its requirement of restocking products.

### Decision
The `Product.Consumer` service will make a synchronous API call to the `SaleOrders.WebApi` to fetch the required product details for the given `OrderId`.

This requires a new endpoint to be created in `SaleOrders.WebApi` that can expose these details.

### Rationale
This approach is chosen for the following reasons:
1.  **Respects Bounded Contexts**: It avoids direct database dependencies between the `Product` and `Order` services. Each service remains the single source of truth for its own data, which is a core principle of Domain-Driven Design and Clean Architecture.
2.  **Avoids Event Bloat**: While the `OrderCancelled` event could be enriched with product details, this would make the event payload significantly larger. Not all potential subscribers to this event may need the product list, so keeping the event lean is preferable.
3.  **Standard Microservice Pattern**: A service consuming an event and then calling back to another service for more data (a pattern sometimes called "Query back") is a common and acceptable pattern in microservice architectures when dealing with data owned by another service.

### Alternatives Considered
-   **Enriching the `OrderCancelled` Event**: This would involve adding the list of products and quantities directly to the event payload. This was rejected to maintain a lean event message and avoid coupling the event structure too tightly to the needs of one specific consumer.
-   **Shared Database/View**: This would involve creating a database view or table that both services could access. This was rejected as it creates strong data-level coupling and violates the principle of each bounded context owning its own data.

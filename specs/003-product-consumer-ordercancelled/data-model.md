# Data Model: Product Stock Restoration

This document outlines the data models involved in the product stock restoration feature.

## Local Model (Product Context)

The core data model within the `Product` bounded context is the `Product` aggregate itself. This feature will primarily interact with its stock-keeping properties.

### Product Aggregate
-   **Project**: `SaleProducts.Domains`
-   **Entity**: `Product`
-   **Relevant Property**: `Stock` (or `StockQuantity`)
-   **Operation**: The `RestockProductCommand` handler will be responsible for loading the `Product` aggregate and calling a method on it to increase the stock quantity.

## Remote Model (Data Transfer Object)

To facilitate the communication between the `Product.Consumer` and the `SaleOrders.WebApi`, a new Data Transfer Object (DTO) is required. This DTO will be the contract for the API call that retrieves order details.

### OrderDetailsResponse DTO

This DTO will be defined in a shared `BC-Contracts` project to be referenced by both the `SaleOrders.WebApi` (as an output) and the `Product` context (as an input).

-   **Namespace**: `Lab.MessageSchemas.Orders.DataTransferObjects`
-   **File**: `OrderDetailsResponse.cs`

```csharp
namespace Lab.MessageSchemas.Orders.DataTransferObjects;

public record OrderDetailsResponse
{
    public Guid OrderId { get; init; }
    public List<LineItemDto> LineItems { get; init; } = new();
}

public record LineItemDto
{
    public Guid ProductId { get; init; }
    public int Quantity { get; init; }
}
```

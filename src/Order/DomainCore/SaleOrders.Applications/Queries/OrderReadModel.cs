namespace SaleOrders.Applications.Queries;

/// <summary>Read-only representation of an Order used by query use cases.</summary>
public sealed record OrderReadModel(
    Guid Id,
    DateTime OrderDate,
    decimal TotalAmount,
    Guid ProductId,
    string ProductName,
    int Quantity);

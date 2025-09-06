namespace Lab.MessageSchemas.Products.IntegrationEvents;

public record ProductItem(Guid ProductId, int Quantity);

public record ProductStockDeducted(
    Guid OrderId,
    List<ProductItem> Products);

public record ProductStockDeductionFailed(
    Guid OrderId,
    string Reason,
    List<ProductItem> Products);

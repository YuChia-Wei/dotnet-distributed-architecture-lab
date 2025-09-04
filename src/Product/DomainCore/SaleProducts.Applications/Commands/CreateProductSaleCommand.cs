namespace SaleProducts.Applications.Commands;

public record CreateProductSaleCommand(Guid OrderId, string ProductName, int Quantity);
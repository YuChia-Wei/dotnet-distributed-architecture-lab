namespace SaleProducts.Applications.Commands;

public record UpdateProductCommand(Guid Id, string Name, string Description, decimal Price, int Stock);
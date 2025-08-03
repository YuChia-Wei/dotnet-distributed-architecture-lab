namespace SaleProducts.Applications.Commands;

public record CreateProductCommand(string Name, string Description, decimal Price, int Stock);
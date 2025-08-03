namespace SaleProducts.Api.Models;

public record CreateProductRequest(string Name, string Description, decimal Price, int Stock);

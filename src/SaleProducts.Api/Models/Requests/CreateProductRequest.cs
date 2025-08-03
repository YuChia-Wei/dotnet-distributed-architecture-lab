namespace SaleProducts.Api.Models.Requests;

public record CreateProductRequest(string Name, string Description, decimal Price, int Stock);

namespace SaleProducts.Api.Models.Requests;

public record UpdateProductRequest(string Name, string Description, decimal Price, int Stock);

namespace SaleProducts.WebApi.Models.Requests;

public record UpdateProductRequest(string Name, string Description, decimal Price, int Stock);

namespace SaleProducts.WebApi.Models.Requests;

public record CreateProductRequest(string Name, string Description, decimal Price);

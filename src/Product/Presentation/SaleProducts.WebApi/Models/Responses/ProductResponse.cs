namespace SaleProducts.WebApi.Models.Responses;

public record ProductResponse(Guid Id, string Name, string Description, decimal Price);
namespace SaleOrders.WebApi.Models.Responses;

public record OrderResponse(Guid Id, DateTime OrderDate, decimal TotalAmount);
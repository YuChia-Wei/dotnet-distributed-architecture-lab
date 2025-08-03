namespace SaleOrders.WebApi.Models.Requests;

public record CreateOrderRequest(DateTime OrderDate, decimal TotalAmount);

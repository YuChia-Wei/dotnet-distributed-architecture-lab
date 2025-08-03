namespace SaleOrders.WebApi.Models;

public record CreateOrderRequest(DateTime OrderDate, decimal TotalAmount);

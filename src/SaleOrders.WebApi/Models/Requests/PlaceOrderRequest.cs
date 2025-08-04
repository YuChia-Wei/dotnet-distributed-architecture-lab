namespace SaleOrders.WebApi.Models.Requests;

public record PlaceOrderRequest(DateTime OrderDate, decimal TotalAmount, string ProductName, int Quantity);
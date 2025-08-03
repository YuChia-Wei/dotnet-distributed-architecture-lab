namespace SaleOrders.Applications.Commands;

public record CreateOrderCommand(DateTime OrderDate, decimal TotalAmount);
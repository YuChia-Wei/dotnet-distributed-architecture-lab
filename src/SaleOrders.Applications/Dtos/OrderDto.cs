namespace SaleOrders.Applications.Dtos;

public record OrderDto(Guid Id, DateTime OrderDate, decimal TotalAmount);
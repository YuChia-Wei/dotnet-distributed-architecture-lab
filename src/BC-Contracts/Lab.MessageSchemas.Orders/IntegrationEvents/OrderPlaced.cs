namespace Lab.MessageSchemas.Orders.IntegrationEvents;

/// <summary>
/// 下單完成的 integration event
/// </summary>
/// <param name="OrderId">訂單的唯一識別碼</param>
/// <param name="ProductName">產品名稱</param>
/// <param name="Quantity">訂購數量</param>
public record OrderPlaced(Guid OrderId, string ProductName, int Quantity);
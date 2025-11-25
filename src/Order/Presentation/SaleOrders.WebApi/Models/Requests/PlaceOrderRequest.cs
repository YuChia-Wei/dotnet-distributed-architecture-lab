namespace SaleOrders.WebApi.Models.Requests;

public record PlaceOrderRequest
{
    public PlaceOrderRequest(DateTime OrderDate, decimal TotalAmount, Guid productId, string ProductName, int Quantity)
    {
        this.OrderDate = OrderDate;
        this.TotalAmount = TotalAmount;
        this.ProductName = ProductName;
        this.Quantity = Quantity;
        this.ProductId = productId;
    }

    public Guid ProductId { get; }

    // [DefaultValue("2025-11-25T12:00:00")]
    public DateTime OrderDate { get; }

    public decimal TotalAmount { get; }

    public string ProductName { get; }

    public int Quantity { get; }
}
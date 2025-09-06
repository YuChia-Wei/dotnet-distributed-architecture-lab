namespace SaleProducts.Applications.Commands;

public record CreateProductSaleCommand
{
    public CreateProductSaleCommand(Guid orderId, Guid productId, string productName, int quantity)
    {
        this.OrderId = orderId;
        this.ProductId = productId;
        this.ProductName = productName;
        this.Quantity = quantity;
    }

    public Guid ProductId { get; init; }

    public Guid OrderId { get; init; }
    public string ProductName { get; init; }
    public int Quantity { get; init; }

    public void Deconstruct(out Guid OrderId, out string ProductName, out int Quantity)
    {
        OrderId = this.OrderId;
        ProductName = this.ProductName;
        Quantity = this.Quantity;
    }
}
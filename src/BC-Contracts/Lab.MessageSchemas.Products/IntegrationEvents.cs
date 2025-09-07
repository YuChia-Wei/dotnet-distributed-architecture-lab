using Lab.BuildingBlocks.Integrations;

namespace Lab.MessageSchemas.Products.IntegrationEvents;

public record ProductItem(Guid ProductId, int Quantity);

public record ProductStockDeducted : IIntegrationEvent
{
    public ProductStockDeducted(
        Guid OrderId,
        List<ProductItem> Products)
    {
        this.OrderId = OrderId;
        this.Products = Products;
    }

    public Guid OrderId { get; init; }
    public List<ProductItem> Products { get; init; }

    /// <summary>
    /// 發生時間
    /// </summary>
    public DateTime OccurredOn { get; }

    public void Deconstruct(
        out Guid OrderId,
        out List<ProductItem> Products)
    {
        OrderId = this.OrderId;
        Products = this.Products;
    }
}

public record ProductStockDeductionFailed : IIntegrationEvent
{
    public ProductStockDeductionFailed(
        Guid OrderId,
        string Reason,
        List<ProductItem> Products)
    {
        this.OrderId = OrderId;
        this.Reason = Reason;
        this.Products = Products;
    }

    public Guid OrderId { get; init; }
    public string Reason { get; init; }
    public List<ProductItem> Products { get; init; }

    /// <summary>
    /// 發生時間
    /// </summary>
    public DateTime OccurredOn { get; }

    public void Deconstruct(
        out Guid OrderId,
        out string Reason,
        out List<ProductItem> Products)
    {
        OrderId = this.OrderId;
        Reason = this.Reason;
        Products = this.Products;
    }
}
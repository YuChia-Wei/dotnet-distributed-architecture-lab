using Lab.BuildingBlocks.Domains;

namespace SaleProducts.Domains;

public class ProductSale : ValueObject
{
    public Guid OrderId { get; private set; }
    public int Quantity { get; private set; }
    public DateTime SaleDate { get; private set; }

    private ProductSale() { }

    public ProductSale(Guid orderId, int quantity)
    {
        OrderId = orderId;
        Quantity = quantity;
        SaleDate = DateTime.UtcNow;
    }

    protected override IEnumerable<object> GetEqualityComponents()
    {
        yield return OrderId;
        yield return Quantity;
        yield return SaleDate;
    }
}

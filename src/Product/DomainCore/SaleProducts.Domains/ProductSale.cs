using Lab.BuildingBlocks.Domains;

namespace SaleProducts.Domains;

public class ProductSale : ValueObject
{
    private ProductSale() { }

    public ProductSale(Guid orderId, int quantity)
    {
        this.OrderId = orderId;
        this.Quantity = quantity;
        this.SaleDate = DateTime.UtcNow;
    }

    public Guid OrderId { get; private set; }
    public int Quantity { get; private set; }
    public DateTime SaleDate { get; private set; }

    public override IEnumerable<object> GetEqualityComponents()
    {
        yield return this.OrderId;
        yield return this.Quantity;
        yield return this.SaleDate;
    }
}
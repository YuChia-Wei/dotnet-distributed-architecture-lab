using Lab.BuildingBlocks.Domains;

namespace SaleProducts.Domains;

/// <summary>
/// 產品銷售紀錄
/// </summary>
public class ProductSaleRecord : ValueObject
{
    /// <summary>
    /// ORM 使用的建構式
    /// </summary>
    private ProductSaleRecord() { }

    public ProductSaleRecord(Guid orderId, int quantity, DateTime saleDate)
    {
        if (orderId == Guid.Empty)
        {
            throw new ArgumentException("OrderId cannot be empty.", nameof(orderId));
        }

        if (quantity <= 0)
        {
            throw new ArgumentOutOfRangeException(nameof(quantity), "Quantity must be positive.");
        }

        this.OrderId = orderId;
        this.Quantity = quantity;
        this.SaleDate = saleDate;
    }

    /// <summary>
    /// 售出的訂單編號
    /// </summary>
    public Guid OrderId { get; private set; }

    /// <summary>
    /// 銷售數量
    /// </summary>
    public int Quantity { get; private set; }

    /// <summary>
    /// 銷售日期
    /// </summary>
    public DateTime SaleDate { get; private set; }

    public override IEnumerable<object> GetEqualityComponents()
    {
        yield return this.OrderId;
        yield return this.Quantity;
        yield return this.SaleDate;
    }
}
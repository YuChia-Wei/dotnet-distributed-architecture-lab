using Lab.BuildingBlocks.Domains;
using SaleOrders.Domains.DomainEvents;

namespace SaleOrders.Domains;

public class Order : AggregateRoot<Guid>
{
    /// <summary>
    /// ctor (for ORM)
    /// </summary>
    private Order(Guid productId)
    {
        this.ProductId = productId;
        this.Status = OrderStatus.Placed;
    }

    /// <summary>
    /// 建立訂單的建構式
    /// </summary>
    /// <param name="orderDate">訂單日期</param>
    /// <param name="totalAmount">訂單總金額</param>
    /// <param name="productId"></param>
    /// <param name="productName">產品名稱</param>
    /// <param name="quantity">數量</param>
    public Order(DateTime orderDate, decimal totalAmount, Guid productId, string productName, int quantity)
    {
        this.Id = Guid.CreateVersion7();
        this.OrderDate = orderDate;
        this.TotalAmount = totalAmount;
        this.ProductId = productId;
        this.ProductName = productName;
        this.Quantity = quantity;
        this.Status = OrderStatus.Placed;

        this.AddDomainEvent(new OrderPlacedDomainEvent(this.Id, this.OrderDate, this.TotalAmount, this.ProductName, this.Quantity, DateTime.UtcNow));
    }

    /// <summary>
    /// 產品識別碼
    /// </summary>
    public Guid ProductId { get; }

    /// <summary>
    /// 產品名稱
    /// </summary>
    public string ProductName { get; }

    /// <summary>
    /// 訂購數量
    /// </summary>
    public int Quantity { get; }

    /// <summary>
    /// 訂單日期
    /// </summary>
    public DateTime OrderDate { get; private set; }

    /// <summary>
    /// 訂單總金額
    /// </summary>
    public decimal TotalAmount { get; private set; }

    /// <summary>
    /// 訂單狀態
    /// </summary>
    public OrderStatus Status { get; private set; } = OrderStatus.Placed;

    /// <summary>
    /// 取消訂單
    /// </summary>
    public void Cancel()
    {
        this.Status = OrderStatus.Cancelled;
        this.AddDomainEvent(new OrderCancelledDomainEvent(this.Id, DateTime.UtcNow));
    }
}

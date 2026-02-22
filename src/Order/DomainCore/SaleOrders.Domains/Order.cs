using Lab.BuildingBlocks.Domains;
using SaleOrders.Domains.DomainEvents;

namespace SaleOrders.Domains;

public class Order : EsAggregateRoot<Guid>
{
    /// <summary>
    /// 事件重播用建構子
    /// </summary>
    public Order(IEnumerable<IDomainEvent> events) : base(events)
    {
    }

    /// <summary>
    /// ORM / 框架用無參數建構子
    /// </summary>
    public Order()
    {
    }

    /// <summary>
    /// 建立訂單的建構式
    /// </summary>
    /// <param name="orderDate">訂單日期</param>
    /// <param name="totalAmount">訂單總金額</param>
    /// <param name="productId">產品識別碼</param>
    /// <param name="productName">產品名稱</param>
    /// <param name="quantity">數量</param>
    public Order(DateTime orderDate, decimal totalAmount, Guid productId, string productName, int quantity)
    {
        Apply(new OrderPlacedDomainEvent(Guid.CreateVersion7(), orderDate, totalAmount, productId, productName, quantity, DateTime.UtcNow));
    }

    /// <summary>
    /// 產品識別碼
    /// </summary>
    public Guid ProductId { get; private set; }

    /// <summary>
    /// 產品名稱
    /// </summary>
    public string ProductName { get; private set; }

    /// <summary>
    /// 訂購數量
    /// </summary>
    public int Quantity { get; private set; }

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
        if (this.Status == OrderStatus.Cancelled)
        {
            return;
        }

        Apply(new OrderCancelledDomainEvent(this.Id, DateTime.UtcNow));
    }

    /// <summary>
    /// 設定訂單為已完成交付
    /// </summary>
    public void Deliver()
    {
        if (this.Status == OrderStatus.Delivered)
        {
            return;
        }

        Apply(new OrderDeliveredDomainEvent(this.Id, DateTime.UtcNow));
    }

    /// <summary>
    /// 設定訂單為已出貨
    /// </summary>
    public void Ship()
    {
        if (this.Status == OrderStatus.Shipped)
        {
            return;
        }

        Apply(new OrderShippedDomainEvent(this.Id, DateTime.UtcNow));
    }

    /// <summary>
    /// 根據領域事件變更聚合根內部狀態
    /// </summary>
    protected override void When(IDomainEvent @event)
    {
        switch (@event)
        {
            case OrderPlacedDomainEvent e:
                this.Id = e.OrderId;
                this.OrderDate = e.OrderDate;
                this.TotalAmount = e.TotalAmount;
                this.ProductId = e.ProductId;
                this.ProductName = e.ProductName;
                this.Quantity = e.Quantity;
                this.Status = OrderStatus.Placed;
                break;

            case OrderCancelledDomainEvent:
                this.Status = OrderStatus.Cancelled;
                break;

            case OrderShippedDomainEvent:
                this.Status = OrderStatus.Shipped;
                break;

            case OrderDeliveredDomainEvent:
                this.Status = OrderStatus.Delivered;
                break;
        }
    }
}
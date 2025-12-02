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
    /// ctor (for Event Sourcing)
    /// </summary>
    public Order() { }

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
        var @event = new OrderPlacedDomainEvent(Guid.CreateVersion7(), orderDate, totalAmount, productId, productName, quantity, DateTime.UtcNow);
        this.AddDomainEvent(@event);
        this.Mutate(@event);
    }

    public int Version { get; private set; }

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

        var @event = new OrderCancelledDomainEvent(this.Id, DateTime.UtcNow);
        this.AddDomainEvent(@event);
        this.Mutate(@event);
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

        var @event = new OrderShippedDomainEvent(this.Id, DateTime.UtcNow);
        this.AddDomainEvent(@event);
        this.Mutate(@event);
    }

    public void LoadFromHistory(IEnumerable<IDomainEvent> history)
    {
        foreach (var e in history)
        {
            this.Mutate(e);
            this.Version++;
        }
    }

    private void Mutate(IDomainEvent @event)
    {
        ((dynamic)this).When((dynamic)@event);
    }

    private void When(OrderPlacedDomainEvent @event)
    {
        this.Id = @event.OrderId;
        this.OrderDate = @event.OrderDate;
        this.TotalAmount = @event.TotalAmount;
        this.ProductId = @event.ProductId;
        this.ProductName = @event.ProductName;
        this.Quantity = @event.Quantity;
        this.Status = OrderStatus.Placed;
    }

    private void When(OrderCancelledDomainEvent @event)
    {
        this.Status = OrderStatus.Cancelled;
    }

    private void When(OrderShippedDomainEvent @event)
    {
        this.Status = OrderStatus.Shipped;
    }
}
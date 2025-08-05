using Lab.BuildingBlocks.Domains;
using SaleOrders.Domains.DomainEvents;

namespace SaleOrders.Domains;

public class Order : AggregateRoot<Guid>
{
    /// <summary>
    /// ctor (for ORM)
    /// </summary>
    private Order()
    {
    }

    public Order(DateTime orderDate, decimal totalAmount, string productName, int quantity)
    {
        this.Id = Guid.CreateVersion7();
        this.OrderDate = orderDate;
        this.TotalAmount = totalAmount;
        this.ProductName = productName;
        this.Quantity = quantity;

        this.AddDomainEvent(new OrderPlacedDomainEvent(this.Id, this.OrderDate, this.TotalAmount, this.ProductName, this.Quantity, DateTime.UtcNow));
    }

    public string ProductName { get; }
    public int Quantity { get; }

    public DateTime OrderDate { get; private set; }
    public decimal TotalAmount { get; private set; }
}
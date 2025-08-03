namespace SaleOrders.Domains;

public class Order
{
    /// <summary>
    /// ctor (for ORM)
    /// </summary>
    private Order()
    {
    }

    public Order(DateTime orderDate, decimal totalAmount)
    {
        this.OrderDate = orderDate;
        this.TotalAmount = totalAmount;
    }

    public DateTime OrderDate { get; private set; }
    public decimal TotalAmount { get; private set; }
    public Guid Id { get; private set; } = Guid.CreateVersion7();
}
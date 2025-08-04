namespace SaleOrders.Domains;

public class Order
{
    /// <summary>
    /// ctor (for ORM)
    /// </summary>
    private Order()
    {
    }

    public Order(DateTime orderDate, decimal totalAmount, string productName, int quantity)
    {
        this.OrderDate = orderDate;
        this.TotalAmount = totalAmount;
        this.ProductName = productName;
        this.Quantity = quantity;
    }

    public string ProductName { get; }
    public int Quantity { get; }

    public DateTime OrderDate { get; private set; }
    public decimal TotalAmount { get; private set; }
    public Guid Id { get; private set; } = Guid.CreateVersion7();
}
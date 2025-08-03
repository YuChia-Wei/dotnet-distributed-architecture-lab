namespace SaleProducts.Domains;

public class Product
{
    /// <summary>
    /// ctor (for ORM)
    /// </summary>
    private Product() { }

    public Product(string name, string description, decimal price, int stock)
    {
        this.Id = Guid.NewGuid();
        this.Name = name;
        this.Description = description;
        this.Price = price;
        this.Stock = stock;
    }

    public string Name { get; private set; }
    public string Description { get; private set; }
    public decimal Price { get; private set; }
    public int Stock { get; private set; }

    public Guid Id { get; private set; }

    /// <summary>
    /// Reduces the product's stock by the specified quantity.
    /// </summary>
    /// <param name="quantity">The amount by which to decrease the stock.</param>
    /// <exception cref="InvalidOperationException">Thrown when the specified quantity is greater than the current stock.</exception>
    public void DecreaseStock(int quantity)
    {
        if (this.Stock < quantity)
        {
            throw new InvalidOperationException("Not enough stock.");
        }

        this.Stock -= quantity;
    }

    /// <summary>
    /// Increases the product's stock by the specified quantity.
    /// </summary>
    /// <param name="quantity">The amount by which to increase the stock.</param>
    public void IncreaseStock(int quantity)
    {
        this.Stock += quantity;
    }

    public void Update(string name, string description, decimal price, int stock)
    {
        this.Name = name;
        this.Description = description;
        this.Price = price;
        this.Stock = stock;
    }
}
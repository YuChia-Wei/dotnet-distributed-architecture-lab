using Lab.BuildingBlocks.Domains;
using SaleProducts.Domains.DomainEvents;

namespace SaleProducts.Domains;

public class Product : AggregateRoot<Guid>
{
    private readonly List<ProductSale> _sales = new();

    /// <summary>
    /// ctor (for ORM)
    /// </summary>
    private Product() { }

    public Product(string name, string description, decimal price, int stock)
    {
        this.Id = Guid.CreateVersion7();
        this.Name = name;
        this.Description = description;
        this.Price = price;
        this.Stock = stock;

        this.AddDomainEvent(new ProductCreated(this.Id, this.Name, this.Price, this.Stock, DateTime.UtcNow));
    }

    public string Name { get; private set; }
    public string Description { get; private set; }
    public decimal Price { get; private set; }
    public int Stock { get; private set; }
    public IReadOnlyCollection<ProductSale> Sales => _sales.AsReadOnly();

    public ProductSale AddSale(Guid orderId, int quantity)
    {
        this.DecreaseStock(quantity);
        var productSale = new ProductSale(orderId, quantity);
        this._sales.Add(productSale);
        return productSale;
    }

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

    public void Delete()
    {
        this.AddDomainEvent(new ProductDeleted(this.Id, DateTime.UtcNow));
    }

    /// <summary>
    /// Increases the product's stock by the specified quantity.
    /// </summary>
    /// <param name="quantity">The amount by which to increase the stock.</param>
    public void IncreaseStock(int quantity)
    {
        this.Stock += quantity;
    }

    /// <summary>
    /// 將商品庫存補回指定數量。
    /// </summary>
    /// <param name="quantity">補回的庫存數量。</param>
    public void Restock(int quantity)
    {
        this.IncreaseStock(quantity);
    }

    public void Update(string name, string description, decimal price, int stock)
    {
        this.Name = name;
        this.Description = description;
        this.Price = price;
        this.Stock = stock;

        this.AddDomainEvent(new ProductUpdated(this.Id, this.Name, this.Description, this.Price, this.Stock, DateTime.UtcNow));
    }
}

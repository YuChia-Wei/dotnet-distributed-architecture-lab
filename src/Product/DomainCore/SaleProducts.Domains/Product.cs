using Lab.BuildingBlocks.Domains;
using SaleProducts.Domains.DomainEvents;

namespace SaleProducts.Domains;

/// <summary>
/// 產品的 Aggregate Root
/// </summary>
public class Product : AggregateRoot<Guid>
{
    /// <summary>
    /// ctor (for ORM)
    /// </summary>
    private Product() { }

    public Product(string name, string description, decimal price)
    {
        this.Id = Guid.CreateVersion7();
        this.Name = name;
        this.Description = description;
        this.Price = price;

        this.AddDomainEvent(new ProductCreated(this.Id, this.Name, this.Price, DateTime.UtcNow));
    }

    public string Name { get; private set; }
    public string Description { get; private set; }
    public decimal Price { get; private set; }

    public void Delete()
    {
        this.AddDomainEvent(new ProductDeleted(this.Id, DateTime.UtcNow));
    }

    public void Update(string name, string description, decimal price)
    {
        this.Name = name;
        this.Description = description;
        this.Price = price;

        this.AddDomainEvent(new ProductUpdated(this.Id, this.Name, this.Description, this.Price, DateTime.UtcNow));
    }
}
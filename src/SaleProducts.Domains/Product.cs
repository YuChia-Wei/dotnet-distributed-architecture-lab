using Lab.SharedKernel.Abstractions;

namespace SaleProducts.Domains;

public class Product : IAggregateRoot
{
    private Product() { }

    public Product(string name, string description, decimal price, int stock)
    {
        this.Id = Guid.NewGuid();
        this.Name = name;
        this.Description = description;
        this.Price = price;
        this.Stock = stock;
    }

    public Guid Id { get; private set; }
    public string Name { get; private set; }
    public string Description { get; private set; }
    public decimal Price { get; private set; }
    public int Stock { get; private set; }

    public object[] GetKeys()
    {
        return new object[]
        {
            this.Id
        };
    }

    public void DecreaseStock(int quantity)
    {
        if (this.Stock < quantity)
        {
            throw new InvalidOperationException("Not enough stock.");
        }

        this.Stock -= quantity;
    }

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
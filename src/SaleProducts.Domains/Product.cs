using Lab.SharedKernel.Abstractions;

namespace SaleProducts.Domains
{
    public class Product : IAggregateRoot
    {
        public Guid Id { get; private set; }
        public string Name { get; private set; }
        public string Description { get; private set; }
        public decimal Price { get; private set; }
        public int Stock { get; private set; }

        private Product() { }

        public Product(string name, string description, decimal price, int stock)
        {
            Id = Guid.NewGuid();
            Name = name;
            Description = description;
            Price = price;
            Stock = stock;
        }

        public void Update(string name, string description, decimal price, int stock)
        {
            Name = name;
            Description = description;
            Price = price;
            Stock = stock;
        }

        public void DecreaseStock(int quantity)
        {
            if (Stock < quantity)
            {
                throw new InvalidOperationException("Not enough stock.");
            }
            Stock -= quantity;
        }

        public void IncreaseStock(int quantity)
        {
            Stock += quantity;
        }

        public object[] GetKeys()
        {
            return new object[] { Id };
        }
    }
}
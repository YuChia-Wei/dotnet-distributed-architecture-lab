using System;
using System.Linq;
using SaleProducts.Domains;
using Xunit;

namespace SaleProducts.Domains.Tests;

public class ProductTests
{
    [Fact]
    public void Ctor_SetsFields_and_Raises_ProductCreated()
    {
        var product = new Product("Name", "Desc", 10m, 5);

        Assert.Equal("Name", product.Name);
        Assert.Equal("Desc", product.Description);
        Assert.Equal(10m, product.Price);
        Assert.Equal(5, product.Stock);
        Assert.Single(product.DomainEvents);
        Assert.Contains(product.DomainEvents, e => e.GetType().Name == "ProductCreated");
    }

    [Fact]
    public void Update_ChangesFields_and_Raises_ProductUpdated()
    {
        var product = new Product("A", "B", 1m, 1);

        product.Update("A2", "B2", 2m, 3);

        Assert.Equal("A2", product.Name);
        Assert.Equal("B2", product.Description);
        Assert.Equal(2m, product.Price);
        Assert.Equal(3, product.Stock);
        Assert.Contains(product.DomainEvents, e => e.GetType().Name == "ProductUpdated");
    }

    [Fact]
    public void DecreaseStock_Reduces_When_Sufficient()
    {
        var product = new Product("A", "B", 1m, 5);
        product.DecreaseStock(3);
        Assert.Equal(2, product.Stock);
    }

    [Fact]
    public void DecreaseStock_Throws_When_Insufficient()
    {
        var product = new Product("A", "B", 1m, 2);
        Assert.Throws<InvalidOperationException>(() => product.DecreaseStock(3));
    }

    [Fact]
    public void IncreaseStock_Increases_By_Quantity()
    {
        var product = new Product("A", "B", 1m, 2);
        product.IncreaseStock(4);
        Assert.Equal(6, product.Stock);
    }

    [Fact]
    public void Restock_Increases_By_Quantity()
    {
        var product = new Product("A", "B", 1m, 5);

        product.Restock(3);

        Assert.Equal(8, product.Stock);
    }
}

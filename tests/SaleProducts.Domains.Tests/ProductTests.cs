using Xunit;

namespace SaleProducts.Domains.Tests;

public class ProductTests
{
    [Fact]
    public void Ctor_SetsFields_and_Raises_ProductCreated()
    {
        var product = new Product("Name", "Desc", 10m);

        Assert.Equal("Name", product.Name);
        Assert.Equal("Desc", product.Description);
        Assert.Equal(10m, product.Price);
        Assert.Single(product.DomainEvents);
        Assert.Contains(product.DomainEvents, e => e.GetType().Name == "ProductCreated");
    }

    [Fact]
    public void Update_ChangesFields_and_Raises_ProductUpdated()
    {
        var product = new Product("A", "B", 1m);

        product.Update("A2", "B2", 2m);

        Assert.Equal("A2", product.Name);
        Assert.Equal("B2", product.Description);
        Assert.Equal(2m, product.Price);
        Assert.Contains(product.DomainEvents, e => e.GetType().Name == "ProductUpdated");
    }
}
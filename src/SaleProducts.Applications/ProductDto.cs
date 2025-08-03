namespace SaleProducts.Applications
{
    public record ProductDto(Guid Id, string Name, string Description, decimal Price, int Stock);
}
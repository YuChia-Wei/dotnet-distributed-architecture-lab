using SaleProducts.Applications.Repositories;
using SaleProducts.Applications.Dtos;

namespace SaleProducts.Applications.Commands;

public class CreateProductSaleCommandHandler
{
    private readonly IProductRepository _productRepository;

    public CreateProductSaleCommandHandler(IProductRepository productRepository)
    {
        _productRepository = productRepository;
    }

    public async Task<ProductSaleDto> Handle(CreateProductSaleCommand request)
    {
        var product = await _productRepository.GetByNameAsync(request.ProductName);

        if (product is null)
        {
            throw new InvalidOperationException($"Product with name {request.ProductName} not found.");
        }

        var productSale = product.AddSale(request.OrderId, request.Quantity);

        await _productRepository.UpdateAsync(product);

        return new ProductSaleDto
        {
            OrderId = productSale.OrderId,
            Quantity = productSale.Quantity,
            SaleDate = productSale.SaleDate
        };
    }
}

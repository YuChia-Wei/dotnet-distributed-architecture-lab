using SaleProducts.Applications.Dtos;
using SaleProducts.Applications.Repositories;

namespace SaleProducts.Applications.Commands;

public class CreateProductSaleCommandHandler
{
    private readonly IProductDomainRepository _productDomainRepository;

    public CreateProductSaleCommandHandler(IProductDomainRepository productDomainRepository)
    {
        this._productDomainRepository = productDomainRepository;
    }

    public async Task<ProductSaleDto> Handle(CreateProductSaleCommand request)
    {
        var product = await this._productDomainRepository.GetByIdAsync(request.OrderId);

        if (product is null)
        {
            throw new InvalidOperationException($"Product with name {request.ProductName} not found.");
        }

        var productSale = product.AddSale(request.OrderId, request.Quantity);

        await this._productDomainRepository.UpdateAsync(product);

        return new ProductSaleDto
        {
            OrderId = productSale.OrderId,
            Quantity = productSale.Quantity,
            SaleDate = productSale.SaleDate
        };
    }
}
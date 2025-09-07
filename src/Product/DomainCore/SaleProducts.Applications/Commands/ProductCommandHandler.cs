using Lab.BuildingBlocks.Integrations;
using Lab.MessageSchemas.Products.IntegrationEvents;
using SaleProducts.Applications.Dtos;
using SaleProducts.Applications.Repositories;
using SaleProducts.Domains;

namespace SaleProducts.Applications.Commands;

public class ProductCommandHandler
{
    public static async Task<ProductSaleDto> Handle(
        CreateProductSaleCommand request,
        IProductDomainRepository productDomainRepository,
        IIntegrationEventPublisher publisher)
    {
        var product = await productDomainRepository.GetByIdAsync(request.ProductId);

        if (product is null)
        {
            throw new InvalidOperationException($"Product with name {request.ProductName} not found.");
        }

        var productSale = product.AddSale(request.OrderId, request.Quantity);

        await productDomainRepository.UpdateAsync(product);

        var productStockDeducted = new ProductStockDeducted(request.OrderId, new List<ProductItem>
        {
            new ProductItem(request.ProductId, request.Quantity)
        });

        await publisher.PublishAsync(productStockDeducted);

        return new ProductSaleDto
        {
            OrderId = productSale.OrderId,
            Quantity = productSale.Quantity,
            SaleDate = productSale.SaleDate
        };
    }

    public static async Task<ProductDto> Handle(CreateProductCommand command, IProductDomainRepository repository)
    {
        var product = new Product(command.Name, command.Description, command.Price, command.Stock);
        await repository.AddAsync(product);
        return new ProductDto(product.Id, product.Name, product.Description, product.Price, product.Stock);
    }

    public static async Task Handle(UpdateProductCommand command, IProductDomainRepository repository)
    {
        var product = await repository.GetByIdAsync(command.Id);
        if (product == null)
        {
            throw new KeyNotFoundException($"Product with ID {command.Id} not found.");
        }

        product.Update(command.Name, command.Description, command.Price, command.Stock);
        await repository.UpdateAsync(product);
    }

    public static async Task Handle(DeleteProductCommand command, IProductDomainRepository repository)
    {
        var product = await repository.GetByIdAsync(command.Id);
        if (product == null)
        {
            throw new KeyNotFoundException($"Product with ID {command.Id} not found.");
        }

        await repository.DeleteAsync(command.Id);
    }
}
using MediatR;
using SaleProducts.Applications.Dtos;
using SaleProducts.Applications.Repositories;
using SaleProducts.Domains;

namespace SaleProducts.Applications.Commands;

public class CommandHandlers
    : IRequestHandler<CreateProductCommand, ProductDto>
{
    private readonly IProductDomainRepository _productDomainRepository;

    public CommandHandlers(IProductDomainRepository productDomainRepository)
    {
        this._productDomainRepository = productDomainRepository;
    }

    public async Task<ProductDto> Handle(CreateProductCommand command, CancellationToken cancellationToken)
    {
        var product = new Product(command.Name, command.Description, command.Price, command.Stock);
        await this._productDomainRepository.AddAsync(product);
        return new ProductDto(product.Id, product.Name, product.Description, product.Price, product.Stock);
    }

    public async Task Handle(UpdateProductCommand command, CancellationToken cancellationToken)
    {
        var product = await this._productDomainRepository.GetByIdAsync(command.Id);
        if (product == null)
        {
            throw new KeyNotFoundException($"Product with ID {command.Id} not found.");
        }

        product.Update(command.Name, command.Description, command.Price, command.Stock);
        await this._productDomainRepository.UpdateAsync(product);
    }

    public async Task Handle(DeleteProductCommand command, CancellationToken cancellationToken)
    {
        var product = await this._productDomainRepository.GetByIdAsync(command.Id);
        if (product == null)
        {
            throw new KeyNotFoundException($"Product with ID {command.Id} not found.");
        }

        await this._productDomainRepository.DeleteAsync(command.Id);
    }
}
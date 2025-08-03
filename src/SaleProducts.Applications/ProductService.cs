using SaleProducts.Applications.Commands;
using SaleProducts.Applications.Queries;
using SaleProducts.Domains;

namespace SaleProducts.Applications
{
    public class ProductService
    {
        private readonly IProductRepository _productRepository;

        public ProductService(IProductRepository productRepository)
        {
            _productRepository = productRepository;
        }

        public async Task<ProductDto> Handle(CreateProductCommand command)
        {
            var product = new Product(command.Name, command.Description, command.Price, command.Stock);
            await _productRepository.AddAsync(product);
            return new ProductDto(product.Id, product.Name, product.Description, product.Price, product.Stock);
        }

        public async Task Handle(UpdateProductCommand command)
        {
            var product = await _productRepository.GetByIdAsync(command.Id);
            if (product == null)
            {
                throw new KeyNotFoundException($"Product with ID {command.Id} not found.");
            }
            product.Update(command.Name, command.Description, command.Price, command.Stock);
            await _productRepository.UpdateAsync(product);
        }

        public async Task Handle(DeleteProductCommand command)
        {
            var product = await _productRepository.GetByIdAsync(command.Id);
            if (product == null)
            {
                throw new KeyNotFoundException($"Product with ID {command.Id} not found.");
            }
            await _productRepository.DeleteAsync(command.Id);
        }

        public async Task<ProductDto> Handle(GetProductByIdQuery query)
        {
            var product = await _productRepository.GetByIdAsync(query.Id);
            if (product == null)
            {
                return null; // Or throw an exception, depending on desired behavior
            }
            return new ProductDto(product.Id, product.Name, product.Description, product.Price, product.Stock);
        }

        public async Task<IEnumerable<ProductDto>> Handle(GetAllProductsQuery query)
        {
            var products = await _productRepository.GetAllAsync();
            return products.Select(p => new ProductDto(p.Id, p.Name, p.Description, p.Price, p.Stock));
        }
    }
}
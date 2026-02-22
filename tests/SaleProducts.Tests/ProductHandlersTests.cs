using Lab.BuildingBlocks.Application;
using SaleProducts.Applications.Commands;
using SaleProducts.Applications.Dtos;
using SaleProducts.Applications.Queries;
using SaleProducts.Domains;
using SaleProducts.Domains.DomainEvents;

namespace SaleProducts.Tests;

public class ProductHandlersTests
{
    [Fact]
    public async Task DeleteCommand_UsesAggregateDelete_AndSave()
    {
        var product = new Product("N", "D", 1m);
        product.ClearDomainEvents();
        var repository = new FakeProductRepository(product);

        await ProductCommandsHandler.HandleAsync(new DeleteProductCommand(product.Id), repository);

        Assert.Contains(product.DomainEvents, e => e is ProductDeleted);
        Assert.Equal(1, repository.SaveCalls);
    }

    [Fact]
    public async Task QueryHandler_UsesQueryService_ForGetAll()
    {
        var service = new FakeProductQueryService
        {
            All = new List<ProductDto>
            {
                new(Guid.NewGuid(), "A", "B", 1m)
            }
        };

        var result = await ProductQueryHandler.Handle(new GetAllProductsQuery(), service);

        Assert.Single(result);
        Assert.Equal(1, service.GetAllCalls);
    }

    [Fact]
    public async Task QueryHandler_Throws_WhenByIdNotFound()
    {
        var service = new FakeProductQueryService();

        await Assert.ThrowsAsync<KeyNotFoundException>(() =>
            ProductQueryHandler.Handle(new GetProductByIdQuery(Guid.NewGuid()), service));
    }

    private sealed class FakeProductRepository : IDomainRepository<Product, Guid>
    {
        private readonly Dictionary<Guid, Product> _products = new();

        public FakeProductRepository(Product seed)
        {
            _products[seed.Id] = seed;
        }

        public int SaveCalls { get; private set; }

        public Task<Product?> FindByIdAsync(Guid id, CancellationToken cancellationToken = default)
        {
            _products.TryGetValue(id, out var product);
            return Task.FromResult(product);
        }

        public Task<IEnumerable<Product>> FindByIdsAsync(IEnumerable<Guid> ids, CancellationToken cancellationToken = default)
        {
            var list = ids.Select(id => _products.TryGetValue(id, out var p) ? p : null)
                .Where(p => p is not null)
                .Cast<Product>()
                .ToList();
            return Task.FromResult<IEnumerable<Product>>(list);
        }

        public Task SaveAsync(Product entity, CancellationToken cancellationToken = default)
        {
            SaveCalls++;
            _products[entity.Id] = entity;
            return Task.CompletedTask;
        }

        public async Task SaveAllAsync(IEnumerable<Product> entities, CancellationToken cancellationToken = default)
        {
            foreach (var entity in entities)
            {
                await SaveAsync(entity, cancellationToken);
            }
        }

        public Task DeleteAsync(Product entity, CancellationToken cancellationToken = default)
        {
            _products.Remove(entity.Id);
            return Task.CompletedTask;
        }
    }

    private sealed class FakeProductQueryService : IProductQueryService
    {
        public IReadOnlyList<ProductDto> All { get; set; } = Array.Empty<ProductDto>();
        public int GetAllCalls { get; private set; }

        public Task<IReadOnlyList<ProductDto>> GetAllAsync(CancellationToken cancellationToken = default)
        {
            GetAllCalls++;
            return Task.FromResult(All);
        }

        public Task<ProductDto?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default)
            => Task.FromResult<ProductDto?>(null);
    }
}

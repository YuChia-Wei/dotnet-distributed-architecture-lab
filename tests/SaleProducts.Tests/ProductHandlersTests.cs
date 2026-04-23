using Lab.BuildingBlocks.Application;
using SaleProducts.Applications.Dtos;
using SaleProducts.Applications.Queries;
using SaleProducts.Applications.UseCases;
using SaleProducts.Domains;
using SaleProducts.Domains.DomainEvents;

namespace SaleProducts.Tests;

/// <summary>
/// 驗證 Product use case 的行為測試。
/// </summary>
public class ProductUseCasesTests
{
    /// <summary>
    /// 驗證刪除產品 use case 會呼叫 aggregate 刪除邏輯並保存結果。
    /// </summary>
    [Fact]
    public async Task DeleteUseCase_UsesAggregateDelete_AndSave()
    {
        var product = new Product("N", "D", 1m);
        product.ClearDomainEvents();
        var repository = new FakeProductRepository(product);
        var useCase = new DeleteProductUseCase(repository);

        await useCase.ExecuteAsync(new DeleteProductInput(product.Id));

        Assert.Contains(product.DomainEvents, e => e is ProductDeleted);
        Assert.Equal(1, repository.SaveCalls);
    }

    /// <summary>
    /// 驗證取得所有產品 use case 會委派給 query service。
    /// </summary>
    [Fact]
    public async Task GetAllProductsUseCase_UsesQueryService()
    {
        var service = new FakeProductQueryService
        {
            All = new List<ProductDto>
            {
                new(Guid.NewGuid(), "A", "B", 1m)
            }
        };
        var useCase = new GetAllProductsUseCase(service);

        var result = await useCase.ExecuteAsync(new GetAllProductsInput());

        Assert.Single(result);
        Assert.Equal(1, service.GetAllCalls);
    }

    /// <summary>
    /// 驗證取得單一產品 use case 在找不到資料時會拋出例外。
    /// </summary>
    [Fact]
    public async Task GetProductByIdUseCase_Throws_WhenByIdNotFound()
    {
        var service = new FakeProductQueryService();
        var useCase = new GetProductByIdUseCase(service);

        await Assert.ThrowsAsync<KeyNotFoundException>(() =>
            useCase.ExecuteAsync(new GetProductByIdInput(Guid.NewGuid())));
    }

    /// <summary>
    /// 提供 Product use case 測試使用的假儲存庫。
    /// </summary>
    private sealed class FakeProductRepository : IDomainRepository<Product, Guid>
    {
        private readonly Dictionary<Guid, Product> _products = new();

        /// <summary>
        /// 初始化假儲存庫並載入種子產品。
        /// </summary>
        /// <param name="seed">初始產品資料。</param>
        public FakeProductRepository(Product seed)
        {
            _products[seed.Id] = seed;
        }

        /// <summary>
        /// 取得儲存動作被呼叫的次數。
        /// </summary>
        public int SaveCalls { get; private set; }

        /// <summary>
        /// 依識別碼查詢產品。
        /// </summary>
        /// <param name="id">產品識別碼。</param>
        /// <param name="cancellationToken">取消權杖。</param>
        /// <returns>查詢到的產品；若不存在則為 <see langword="null"/>。</returns>
        public Task<Product?> FindByIdAsync(Guid id, CancellationToken cancellationToken = default)
        {
            _products.TryGetValue(id, out var product);
            return Task.FromResult(product);
        }

        /// <summary>
        /// 依多個識別碼查詢產品集合。
        /// </summary>
        /// <param name="ids">產品識別碼集合。</param>
        /// <param name="cancellationToken">取消權杖。</param>
        /// <returns>符合條件的產品集合。</returns>
        public Task<IEnumerable<Product>> FindByIdsAsync(IEnumerable<Guid> ids, CancellationToken cancellationToken = default)
        {
            var list = ids.Select(id => _products.TryGetValue(id, out var p) ? p : null)
                .Where(p => p is not null)
                .Cast<Product>()
                .ToList();
            return Task.FromResult<IEnumerable<Product>>(list);
        }

        /// <summary>
        /// 保存單一產品。
        /// </summary>
        /// <param name="entity">要保存的產品。</param>
        /// <param name="cancellationToken">取消權杖。</param>
        public Task SaveAsync(Product entity, CancellationToken cancellationToken = default)
        {
            SaveCalls++;
            _products[entity.Id] = entity;
            return Task.CompletedTask;
        }

        /// <summary>
        /// 批次保存多個產品。
        /// </summary>
        /// <param name="entities">要保存的產品集合。</param>
        /// <param name="cancellationToken">取消權杖。</param>
        public async Task SaveAllAsync(IEnumerable<Product> entities, CancellationToken cancellationToken = default)
        {
            foreach (var entity in entities)
            {
                await SaveAsync(entity, cancellationToken);
            }
        }

        /// <summary>
        /// 刪除指定產品。
        /// </summary>
        /// <param name="entity">要刪除的產品。</param>
        /// <param name="cancellationToken">取消權杖。</param>
        public Task DeleteAsync(Product entity, CancellationToken cancellationToken = default)
        {
            _products.Remove(entity.Id);
            return Task.CompletedTask;
        }
    }

    /// <summary>
    /// 提供 Product query use case 測試使用的假查詢服務。
    /// </summary>
    private sealed class FakeProductQueryService : IProductQueryService
    {
        /// <summary>
        /// 取得或設定全部產品查詢結果。
        /// </summary>
        public IReadOnlyList<ProductDto> All { get; set; } = Array.Empty<ProductDto>();

        /// <summary>
        /// 取得查詢全部產品被呼叫的次數。
        /// </summary>
        public int GetAllCalls { get; private set; }

        /// <summary>
        /// 取得全部產品資料。
        /// </summary>
        /// <param name="cancellationToken">取消權杖。</param>
        /// <returns>產品 DTO 清單。</returns>
        public Task<IReadOnlyList<ProductDto>> GetAllAsync(CancellationToken cancellationToken = default)
        {
            GetAllCalls++;
            return Task.FromResult(All);
        }

        /// <summary>
        /// 依識別碼取得產品資料。
        /// </summary>
        /// <param name="id">產品識別碼。</param>
        /// <param name="cancellationToken">取消權杖。</param>
        /// <returns>產品 DTO；此測試替身固定回傳 <see langword="null"/>。</returns>
        public Task<ProductDto?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default)
            => Task.FromResult<ProductDto?>(null);
    }
}

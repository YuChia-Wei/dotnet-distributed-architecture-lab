# Code Templates (.NET)

This document contains C# templates and patterns commonly used in the .NET stack.

## Command Handler Template (Wolverine)

```csharp
public sealed record CreateTaskInput(string PlanId, string ProjectName, string TaskName);

public sealed class CreateTaskHandler
{
    private readonly IRepository<Plan, PlanId> _repository;

    public CreateTaskHandler(IRepository<Plan, PlanId> repository)
    {
        Contract.RequireNotNull(nameof(repository), repository);
        _repository = repository;
    }

    public async Task<CqrsOutput> Handle(CreateTaskInput input)
    {
        // 1) Contracts validation (outside try-catch)
        Contract.RequireNotNull(nameof(input), input);
        Contract.RequireNotNull(nameof(input.PlanId), input.PlanId);

        try
        {
            var output = CqrsOutput.Create();

            // Step 1: Load aggregate
            var plan = await _repository.FindByIdAsync(PlanId.ValueOf(input.PlanId));
            if (plan == null)
            {
                return output.Fail("Plan not found");
            }

            // Step 2: Execute business logic
            plan.CreateTask(ProjectName.ValueOf(input.ProjectName), TaskName.ValueOf(input.TaskName));

            // Step 3: Save aggregate
            await _repository.SaveAsync(plan);

            // Step 4: Return success
            return output.Ok(plan.Id.Value);
        }
        catch (Exception ex)
        {
            throw new UseCaseFailureException(ex.Message);
        }
    }
}
```

## Query Handler Template (Projection)

```csharp
public sealed record GetProductInput(string ProductId);
public sealed record GetProductOutput(ProductDto Product, ExitCode ExitCode, string? Message);

public sealed class GetProductHandler
{
    private readonly IProductProjection _projection;

    public GetProductHandler(IProductProjection projection)
    {
        Contract.RequireNotNull(nameof(projection), projection);
        _projection = projection;
    }

    public async Task<GetProductOutput> Handle(GetProductInput input)
    {
        Contract.RequireNotNull(nameof(input), input);

        try
        {
            var dto = await _projection.FindByIdAsync(input.ProductId);
            if (dto == null)
            {
                return new GetProductOutput(default!, ExitCode.FAILURE, "Product not found");
            }

            return new GetProductOutput(dto, ExitCode.SUCCESS, null);
        }
        catch (Exception ex)
        {
            throw new UseCaseFailureException(ex.Message);
        }
    }
}
```

## Validation Pattern

### Aggregate Root Validation
```csharp
Contract.RequireNotNull(nameof(productId), productId);
Contract.Require(name.Length <= 100, "name exceeds maximum length");
```

### Entity & Value Object Validation
```csharp
Objects.RequireNotNull(pbiId, "pbiId cannot be null");
Objects.RequireNotNull(name, "name cannot be null");
```

### Constructor Validation
```csharp
public CreateProductHandler(IRepository<Product, ProductId> repository)
{
    Contract.RequireNotNull(nameof(repository), repository);
    _repository = repository;
}
```

## Aggregate Constructor Template

```csharp
public sealed class Product : AggregateRoot<ProductId>
{
    public Product(ProductId productId, ProductName name)
    {
        Contract.RequireNotNull(nameof(productId), productId);
        Contract.RequireNotNull(nameof(name), name);
        Apply(new ProductCreated(productId, name, metadata: new Dictionary<string, string>(), DateProvider.Now()));
    }
}

// ❌ WRONG: Static factory hides event sourcing rules
// public static Product Create(...) { ... }
```

## Domain Event Template

```csharp
public sealed record ProductCreated(
    ProductId ProductId,
    ProductName Name,
    IReadOnlyDictionary<string, string> Metadata,
    Guid Id,
    DateTimeOffset OccurredOn
)
{
    public ProductCreated
    {
        Contract.RequireNotNull(nameof(ProductId), ProductId);
        Contract.RequireNotNull(nameof(Name), Name);
        Contract.RequireNotNull(nameof(Metadata), Metadata); // Required
        Contract.RequireNotNull(nameof(Id), Id);
        Contract.RequireNotNull(nameof(OccurredOn), OccurredOn);
    }
}
```

## Use Case Interface Pattern (Optional)

```csharp
public interface ICreateProductUseCase
{
    Task<CqrsOutput> Execute(CreateProductInput input);
}
```

## Repository Usage Template

```csharp
public sealed class CreateProductHandler
{
    private readonly IRepository<Product, ProductId> _repository;

    public CreateProductHandler(IRepository<Product, ProductId> repository)
    {
        _repository = repository;
    }
}

// ❌ DO NOT create custom repository interfaces for domain writes
// public interface ProductRepository : IRepository<Product, ProductId> { }
```

## Projection Template (EF Core)

```csharp
public interface IProductProjection
{
    Task<ProductDto?> FindByIdAsync(string productId);
    Task<IReadOnlyList<ProductDto>> FindAllAsync();
}

public sealed class EfProductProjection : IProductProjection
{
    private readonly AppDbContext _db;

    public EfProductProjection(AppDbContext db)
    {
        _db = db;
    }

    public async Task<ProductDto?> FindByIdAsync(string productId)
    {
        return await _db.Products
            .Where(p => p.ProductId == productId)
            .Select(ProductMapper.ToDto)
            .FirstOrDefaultAsync();
    }
}
```

## Mapper Template

```csharp
public static class ProductMapper
{
    public static ProductDto ToDto(Product product)
        => new(product.Id.Value, product.Name.Value);
}
```

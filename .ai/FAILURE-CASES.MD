# Common Failure Cases and Anti-Patterns (.NET)

This document catalogs common mistakes and anti-patterns to avoid in the .NET stack.

## Code Generation Failures

### 1. Input/Output File Placement
**❌ WRONG**: Input/Output as inner classes
```csharp
public interface CreateProductUseCase
{
    class Input { }
    class Output { }
}
```

**✅ CORRECT**: Input/Output in separate files
```
src/Product/DomainCore/SaleProducts.Applications/UseCases/CreateProduct/CreateProductInput.cs
src/Product/DomainCore/SaleProducts.Applications/UseCases/CreateProduct/CreateProductOutput.cs
```

### 1.1 Wrong Boundary Naming
**❌ WRONG**: use case boundary models named as DTOs
```csharp
public sealed record CreateProductInputDto(...);
public sealed record CreateProductOutputDto(...);
```

**✅ CORRECT**: use case boundary models use Input/Output naming
```csharp
public sealed record CreateProductInput(...);
public sealed record CreateProductOutput(...);
```

### 1.2 HTTP Controller Dispatching Through Bus
**❌ WRONG**: controller uses `IMessageBus` as the HTTP application boundary
```csharp
public async Task<IActionResult> Create(
    [FromBody] CreateProductRequest request)
{
    var result = await _bus.InvokeAsync<CreateProductOutput>(
        new CreateProductCommand(request.Name));
    return Ok(result);
}
```

**✅ CORRECT**: controller resolves explicit use case via `[FromServices]`
```csharp
public async Task<IActionResult> Create(
    [FromBody] CreateProductRequest request,
    [FromServices] ICreateProductUseCase useCase,
    CancellationToken ct)
{
    var output = await useCase.ExecuteAsync(
        new CreateProductInput(request.Name),
        ct);
    return Ok(new CreateProductResponse(output.Id));
}
```

### 2. Missing Mappers
**❌ WRONG**: DTO without mapper

**✅ CORRECT**: Provide mapper for every DTO
```csharp
public static class ProductMapper
{
    public static ProductDto ToDto(Product product) { }
}
```

### 3. Missing Projection Implementation
**❌ WRONG**: Query handler without Projection

**✅ CORRECT**: Projection interface + EF Core implementation
```csharp
public interface IProductProjection { }
public sealed class EfProductProjection : IProductProjection { }
```

### 4. Wrong Folder Structure
**❌ WRONG**: Multiple aggregates in one folder
```
src/Domain/
  Product.cs
  Sprint.cs
```

**✅ CORRECT**: One aggregate per folder
```
src/Domain/Product/...
src/Domain/Sprint/...
```

### 5. Missing Metadata in Domain Events
**❌ WRONG**: Event without metadata
```csharp
public sealed record PbiCreated(PbiId Id, string Name);
```

**✅ CORRECT**: Include metadata and timestamps
```csharp
public sealed record PbiCreated(
    PbiId Id,
    string Name,
    IReadOnlyDictionary<string, string> Metadata,
    Guid EventId,
    DateTimeOffset OccurredOn);
```

### 6. Wrong Metadata Initialization
**❌ WRONG**: Using immutable or empty metadata
```csharp
var metadata = ImmutableDictionary<string, string>.Empty;
```

**✅ CORRECT**: Use a mutable dictionary and validate non-null
```csharp
var metadata = new Dictionary<string, string>();
```

## Architecture Violations

### 7. Custom Repository Interfaces
**❌ WRONG**: Adding custom methods to repository interfaces
```csharp
public interface IProductRepository : IRepository<Product, ProductId>
{
    Task<IReadOnlyList<Product>> FindByNameAsync(string name);
}
```

**✅ CORRECT**: Use generic repository, queries go to Projection

### 8. Static Factory Methods in Aggregates
**❌ WRONG**: Using static factories for Aggregate creation

**✅ CORRECT**: Use public constructors + Apply/When

### 9. Direct State Assignment in Aggregate
**❌ WRONG**: Setting state in constructor without Apply/When

**✅ CORRECT**: Use Apply/When only

## Testing Failures

### 10. Plain xUnit without BDDfy for Use Case Tests
**❌ WRONG**: Only `[Fact]` with imperative steps

**✅ CORRECT**: BDDfy with Gherkin-style naming
```csharp
[Fact]
public void Rule_Create_product_successfully()
{
    this.Given(_ => Given_valid_input())
        .When(_ => When_execute())
        .Then(_ => Then_success())
        .BDDfy();
}
```

### 11. Command Handler as HTTP Boundary by Default
**❌ WRONG**: treating command handler as the default HTTP use case boundary

**✅ CORRECT**: keep command handlers for message-oriented flows, and use explicit use cases as HTTP inbound ports

### 11. Hardcoding profile in tests
**❌ WRONG**: `ASPNETCORE_ENVIRONMENT` set inside test class

**✅ CORRECT**: Profile set in test runner or fixture

## Outbox Pattern Failures

### 12. OutboxMapper as Separate Class
**❌ WRONG**: Standalone mapper with no inner class adapter

**✅ CORRECT**: Mapper with inner IOutboxMapper adapter

### 13. Missing transient fields in data model
**❌ WRONG**: Not excluding domain event fields from persistence

**✅ CORRECT**: Mark transient fields or configure EF Core to ignore

## Prevention Strategies

1. Use `.ai/assets/` prompts
2. Follow `.ai/DOTNET-CODE-TEMPLATES.md`
3. Read `.dev/standards/coding-standards.md`
4. Run `.ai/scripts/check-all.sh`


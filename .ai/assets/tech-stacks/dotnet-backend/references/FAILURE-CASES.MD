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
src/Application/Product/UseCases/Commands/CreateProductInput.cs
src/Application/Product/UseCases/Commands/CreateProductOutput.cs
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
  Iteration.cs
```

**✅ CORRECT**: One aggregate per folder
```
src/Domain/Product/...
src/Domain/Iteration/...
```

### 5. Missing Metadata in Domain Events
**❌ WRONG**: Event without metadata
```csharp
public sealed record WorkItemCreated(WorkItemId Id, string Name);
```

**✅ CORRECT**: Include metadata and timestamps
```csharp
public sealed record WorkItemCreated(
    WorkItemId Id,
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

### 7. Mixed Repository Responsibilities
**❌ WRONG**: Adding query methods to an aggregate repository
```csharp
public interface IProductRepository : IAggregateRepository<Product, ProductId>
{
    Task<IReadOnlyList<Product>> FindByNameAsync(string name);
}
```

**✅ CORRECT**: Keep aggregate writes on the aggregate contract and put read
criteria on a read-only query port
```csharp
public interface IProductQueryRepository : IQueryRepository
{
    Task<IReadOnlyList<ProductSummary>> FindByNameAsync(
        string name,
        CancellationToken cancellationToken);
}
```

### 8. Static Factory Methods in Aggregates
**❌ WRONG**: Using static factories for Aggregate creation

**✅ CORRECT**: Use public constructors + Apply/When

### 9. Direct State Assignment in Aggregate
**❌ WRONG**: Setting state in constructor without Apply/When

**✅ CORRECT**: Use Apply/When only

## Testing Failures

### 10. Tests without Given-When-Then Structure
**❌ WRONG**: Plain xUnit organized as Arrange-Act-Assert, or `[Fact]` methods with imperative steps but no explicit GWT structure and naming.

**✅ CORRECT**: GWT structure and naming. BDDfy is the default; plain xUnit GWT is valid only when the target team explicitly opts out of the package.
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
2. Follow `.ai/assets/tech-stacks/dotnet-backend/references/CODE-TEMPLATES.MD`
3. Read `.dev/standards/coding-standards.md`
4. Run `.ai/scripts/check-all.sh`

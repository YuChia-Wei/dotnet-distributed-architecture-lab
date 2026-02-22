# Code Review Checklist Quick Reference (.NET)

## File Type Detection

```
Aggregate Root:
  - src/Domain/**/Aggregates/*.cs
  - Any class inheriting from AggregateRoot<TId>

Domain Event:
  - src/Domain/**/Events/*Events.cs
  - Records implementing IDomainEvent

Entity:
  - src/Domain/**/Entities/*.cs
  - Classes implementing IEntity<TId>

Value Object:
  - src/Domain/**/ValueObjects/*.cs
  - Records or immutable classes

Use Case (Command):
  - src/Application/**/UseCases/Commands/*.cs

Use Case (Query):
  - src/Application/**/UseCases/Queries/*.cs

Controller:
  - src/Api/Controllers/*.cs

Mapper:
  - src/Application/**/Ports/**/*Mapper.cs

Outbox Data:
  - src/Infrastructure/**/Outbox/*Data.cs

Test:
  - tests/**/*.cs
```

---

## Aggregate Pattern Detection (Type-First)

Before applying aggregate checks, determine aggregate pattern with this priority:

1. Type hierarchy (primary):
   - Inherits `EsAggregateRoot<TId>` -> Event Sourcing aggregate
   - Inherits `AggregateRoot<TId>` but not `EsAggregateRoot<TId>` -> State-based aggregate (outbox/inmemory)
2. `.dev/project-config.yaml` (secondary hint):
   - `architecture.aggregates.<AggregateName>.pattern`
   - Fallback: `architecture.defaultPattern`
3. If type and config conflict:
   - Report `TYPE-CONFIG MISMATCH` as MUST FIX
   - Use type hierarchy as final decision for review rules

### Ruleset Selection

| Detected Type | Apply ES checks (`Apply/When`) | Priority |
|---|---|---|
| `EsAggregateRoot<TId>` | Yes | CRITICAL |
| `AggregateRoot<TId>` (non-ES) | No | N/A |

## Aggregate Complete Review Mode

When reviewing an Aggregate, include **all related components** in the same directory.

### Directory Structure
```
src/Domain/<Aggregate>/
├── Aggregates/<Aggregate>.cs     ← Aggregate Root (CRITICAL)
├── Events/<Aggregate>Events.cs   ← Domain Events (CRITICAL)
├── Entities/*.cs                 ← Internal Entities
└── ValueObjects/*.cs             ← Value Objects
```

### Review Priority

| Component | Priority | Checklist Section |
|-----------|----------|-------------------|
| Aggregate Root | CRITICAL | Event Sourcing Compliance |
| Domain Events | CRITICAL | Domain Event Design |
| Internal Entity | HIGH | Entity Design |
| Value Object | MEDIUM | Value Object Design |

### Validation Method by Type

| Type | Use This | Not This |
|------|----------|----------|
| Aggregate Root | Guard Clauses / Contracts | `ArgumentNullException.ThrowIfNull` |
| Entity | `ArgumentNullException.ThrowIfNull` | Guard Clauses |
| Value Object | `ArgumentNullException.ThrowIfNull` | Guard Clauses |
| Domain Event | `ArgumentNullException.ThrowIfNull` | Guard Clauses |

---

## Priority 1: CRITICAL Checks

### Aggregate Root - Event Sourcing Compliance (ES only)

| Check | Correct | Wrong |
|-------|---------|-------|
| State Assignment | Only in `When(event)` method | In constructor or command methods |
| Constructor | Calls `Apply(event)` | Sets state directly |
| Command Methods | Calls `Apply(event)` | Sets state directly |

### Correct Pattern

```csharp
public class Product : EsAggregateRoot<ProductId>
{
    public string Name { get; private set; } = string.Empty;
    public ProductStatus Status { get; private set; }

    // ✅ CORRECT - Constructor uses Apply
    public Product(ProductId id, string name)
    {
        // Guard clause before Apply
        ArgumentNullException.ThrowIfNull(id);
        ArgumentException.ThrowIfNullOrEmpty(name);

        Apply(new ProductCreated(id, name, DateTime.UtcNow));
    }

    // ✅ CORRECT - Command method uses Apply
    public void Rename(string newName)
    {
        ArgumentException.ThrowIfNullOrEmpty(newName);
        Apply(new ProductRenamed(Id, newName, DateTime.UtcNow));
    }

    // ✅ CORRECT - State only set here
    protected override void When(IDomainEvent @event)
    {
        switch (@event)
        {
            case ProductCreated e:
                Id = e.ProductId;
                Name = e.Name;
                Status = ProductStatus.Active;
                break;
            case ProductRenamed e:
                Name = e.NewName;
                break;
        }
    }
}
```

### Wrong Pattern

```csharp
// ❌ WRONG - State set in constructor
public Product(ProductId id, string name)
{
    Id = id;           // FORBIDDEN!
    Name = name;       // FORBIDDEN!
    Status = ProductStatus.Active;  // FORBIDDEN!
}

// ❌ WRONG - State set in command method
public void Rename(string newName)
{
    Name = newName;    // FORBIDDEN!
    AddDomainEvent(new ProductRenamed(Id, newName, DateTime.UtcNow));
}
```

---

### Domain Event Design

| Check | Correct | Wrong |
|-------|---------|-------|
| Definition | `record` | `class` |
| Mutability | Immutable | Has setters |
| Required Fields | Has `OccurredOn`, Aggregate ID | Missing metadata |

### Correct Pattern

```csharp
// ✅ CORRECT - Record with required fields
public sealed record ProductCreated(
    ProductId ProductId,
    string Name,
    DateTime OccurredOn) : IDomainEvent
{
    public Guid EventId { get; } = Guid.NewGuid();
}

public sealed record ProductRenamed(
    ProductId ProductId,
    string NewName,
    DateTime OccurredOn) : IDomainEvent
{
    public Guid EventId { get; } = Guid.NewGuid();
}
```

### Wrong Pattern

```csharp
// ❌ WRONG - Class instead of record
public class ProductCreated : IDomainEvent
{
    public ProductId ProductId { get; set; }  // FORBIDDEN! Has setter
    public string Name { get; set; }          // FORBIDDEN!
}

// ❌ WRONG - Missing OccurredOn
public sealed record ProductCreated(ProductId ProductId, string Name);
```

---

### Entity Design

| Check | Correct | Wrong |
|-------|---------|-------|
| Interface | Implements `IEntity<TId>` | No interface |
| ID | Has unique identifier | No ID field |
| Equality | Based on ID | Default or all fields |
| Validation | `ArgumentNullException.ThrowIfNull` | Guard Clauses |

### Correct Pattern

```csharp
public class Task : IEntity<TaskId>
{
    public TaskId Id { get; private set; }
    public string Name { get; private set; }
    public TaskStatus Status { get; private set; }

    // ✅ CORRECT - Uses ArgumentNullException
    public Task(TaskId id, string name)
    {
        ArgumentNullException.ThrowIfNull(id);
        ArgumentException.ThrowIfNullOrEmpty(name);

        Id = id;
        Name = name;
        Status = TaskStatus.Todo;
    }

    // ✅ CORRECT - Equality based on ID
    public override bool Equals(object? obj)
        => obj is Task other && Id.Equals(other.Id);

    public override int GetHashCode() => Id.GetHashCode();
}
```

---

### Value Object Design

| Check | Correct | Wrong |
|-------|---------|-------|
| Mutability | Immutable (record or readonly) | Has setters |
| Equality | Structural (all fields) | Reference equality |
| Operations | Returns new instance | Mutates self |

### Correct Pattern

```csharp
// ✅ CORRECT - Record-based Value Object
public sealed record ProductId(string Value)
{
    public ProductId() : this(Guid.NewGuid().ToString()) { }

    public static ProductId Create() => new();
    public static ProductId From(string value) => new(value);
}

// ✅ CORRECT - Money Value Object
public sealed record Money(decimal Amount, string Currency)
{
    // Returns new instance
    public Money Add(Money other)
    {
        if (Currency != other.Currency)
            throw new InvalidOperationException("Currency mismatch");
        return this with { Amount = Amount + other.Amount };
    }
}
```

### Wrong Pattern

```csharp
// ❌ WRONG - Mutable
public class Money
{
    public decimal Amount { get; set; }  // FORBIDDEN! Has setter

    public void Add(Money other)  // FORBIDDEN! Mutates self
    {
        Amount += other.Amount;
    }
}
```

---

## Priority 2: MUST FIX Checks

### Use Case Handler Structure

| Check | Correct | Wrong |
|-------|---------|-------|
| DI Registration | Via `IServiceCollection` | Attribute-based `[Service]` |
| Class | Plain POCO | Has DI attributes |
| Return Type | `Task<Result<T>>` or similar | `Task<T>` without error handling |

### Correct Pattern

```csharp
// ✅ CORRECT - Plain POCO, no attributes
public class CreateProductHandler
{
    private readonly IProductRepository _repository;
    private readonly IUnitOfWork _unitOfWork;

    public CreateProductHandler(
        IProductRepository repository,
        IUnitOfWork unitOfWork)
    {
        _repository = repository;
        _unitOfWork = unitOfWork;
    }

    public async Task<Result<ProductId>> Handle(
        CreateProductCommand command,
        CancellationToken ct)
    {
        // Validation
        if (string.IsNullOrEmpty(command.Name))
            return Result.Failure<ProductId>("Name is required");

        // Domain logic
        var product = new Product(ProductId.Create(), command.Name);

        // Persistence
        await _repository.SaveAsync(product, ct);
        await _unitOfWork.CommitAsync(ct);

        return Result.Success(product.Id);
    }
}

// ✅ CORRECT - DI registration in Startup/Program.cs
services.AddScoped<CreateProductHandler>();
```

### Wrong Pattern

```csharp
// ❌ WRONG - Has DI attribute
[Service]  // FORBIDDEN!
public class CreateProductHandler { }

// ❌ WRONG - Registered via attribute scanning
services.Scan(scan => scan
    .FromAssemblies(...)
    .AddClasses(classes => classes.WithAttribute<ServiceAttribute>())
    .AsImplementedInterfaces());
```

---

### Repository Rules

| Check | Correct | Wrong |
|-------|---------|-------|
| Write Interface | `IDomainRepository<TEntity, TId>` | Repository not aligned with shared write contract |
| Domain Wrapper | Optional `I<Domain>DomainRepository : IDomainRepository<...>` and no extra methods | Wrapper adds query/custom methods |
| Query Responsibility | `I<Domain>QueryService` + `I<Domain>QueryRepository` | Query methods mixed into Domain Repository |

### Correct Pattern

```csharp
// ✅ CORRECT - Shared write repository contract
public interface IDomainRepository<TEntity, in TId>
    where TEntity : IAggregateRoot<TId>
    where TId : notnull
{
    Task<TEntity?> FindByIdAsync(TId id, CancellationToken ct = default);
    Task<IEnumerable<TEntity>> FindByIdsAsync(IEnumerable<TId> ids, CancellationToken ct = default);
    Task SaveAsync(TEntity entity, CancellationToken ct = default);
    Task SaveAllAsync(IEnumerable<TEntity> entities, CancellationToken ct = default);
    Task DeleteAsync(TEntity entity, CancellationToken ct = default);
}

// ✅ CORRECT - Domain-specific wrapper (optional, no extra methods)
public interface IProductDomainRepository : IDomainRepository<Product, Guid>
{
}

// ✅ CORRECT - Query side split
public interface IProductQueryRepository
{
    Task<ProductDto?> GetByIdAsync(Guid id, CancellationToken ct = default);
    Task<IReadOnlyList<Guid>> GetIdsByStatusAsync(string status, CancellationToken ct = default);
}

public interface IProductQueryService
{
    Task<ProductDto?> GetByIdAsync(Guid id, CancellationToken ct = default);
    Task<IReadOnlyList<Guid>> GetIdsForCommandAsync(string status, CancellationToken ct = default);
}
```

### Wrong Pattern

```csharp
// ❌ WRONG - Domain wrapper adds forbidden methods
public interface IProductDomainRepository : IDomainRepository<Product, Guid>
{
    Task<Product?> FindByNameAsync(string name);  // FORBIDDEN!
    Task<IEnumerable<Product>> GetActiveProducts();  // FORBIDDEN!
}
```

---

## Priority 3: SHOULD FIX Checks

### Test Structure (xUnit + BDDfy)

| Check | Correct | Wrong |
|-------|---------|-------|
| Framework | xUnit + BDDfy | NUnit, MSTest |
| Naming | Gherkin-style | Technical names |
| Base Class | None | `BaseTestClass` |
| Mocking | NSubstitute | Moq |

### Correct Pattern

```csharp
// ✅ CORRECT - Gherkin-style naming with BDDfy
public class CreateProductTests
{
    [Fact]
    public void GivenValidProductData_WhenCreatingProduct_ThenProductIsCreated()
    {
        this.Given(_ => GivenValidProductData())
            .When(_ => WhenCreatingProduct())
            .Then(_ => ThenProductIsCreated())
            .BDDfy();
    }

    private CreateProductCommand _command = null!;
    private Result<ProductId> _result = null!;
    private readonly IProductRepository _repository = Substitute.For<IProductRepository>();

    private void GivenValidProductData()
    {
        _command = new CreateProductCommand("Test Product");
    }

    private async Task WhenCreatingProduct()
    {
        var handler = new CreateProductHandler(_repository, ...);
        _result = await handler.Handle(_command, CancellationToken.None);
    }

    private void ThenProductIsCreated()
    {
        _result.IsSuccess.Should().BeTrue();
        _result.Value.Should().NotBeNull();
    }
}
```

### Wrong Pattern

```csharp
// ❌ WRONG - Technical naming
[Fact]
public void TestCreateProduct() { }

// ❌ WRONG - Using base class
public class CreateProductTests : BaseTestClass { }  // FORBIDDEN!

// ❌ WRONG - Using Moq
var repository = new Mock<IProductRepository>();  // Use NSubstitute instead
```

---

## Validation Checklist

### Aggregate Root (ES only)
- [ ] State only set in `When()` method
- [ ] Constructor uses `Apply(event)`
- [ ] Command methods use `Apply(event)`
- [ ] No direct state assignment outside `When()`
- [ ] Domain events match switch cases in `When()`

### Aggregate Root (State-based: non-ES)
- [ ] Constructor/command methods enforce invariants
- [ ] State changes are explicit and valid for business rules
- [ ] Domain events are raised for meaningful state transitions
- [ ] No persistence concerns leaking into domain behavior

### Domain Event
- [ ] Defined as `sealed record`
- [ ] Has `OccurredOn` timestamp
- [ ] Has Aggregate ID field
- [ ] Immutable (no setters)

### Entity
- [ ] Implements `IEntity<TId>`
- [ ] Has unique identifier
- [ ] Uses `ArgumentNullException.ThrowIfNull`
- [ ] Equality based on ID

### Value Object
- [ ] Immutable (record or readonly)
- [ ] Operations return new instances
- [ ] Uses structural equality

### Use Case Handler
- [ ] Registered via `IServiceCollection`
- [ ] No DI attributes
- [ ] Returns `Result<T>` or similar

### Repository
- [ ] Write side uses `IDomainRepository<TEntity, TId>`
- [ ] Domain wrapper (if any) does not add extra methods
- [ ] Query methods are in QueryService/QueryRepository, not Domain Repository

### Tests
- [ ] xUnit + BDDfy
- [ ] Gherkin-style naming
- [ ] No `BaseTestClass`
- [ ] NSubstitute for mocking

---

## Priority 2: Mapper Rules

**Location**: `src/Application/<Aggregate>/Ports/`

### Key Rules

| Check | Correct | Wrong |
|-------|---------|-------|
| Location | `Application/<Aggregate>/Ports/` | `Infrastructure/Mappers/` |
| Pattern | Static methods | Instance methods |
| DI | No attributes | `[Service]` attribute |

### Required Methods

```csharp
public static class ProductMapper
{
    // 1. Domain → DTO (API responses)
    public static ProductDto ToDto(Product product) { ... }

    // 2. Data → DTO (Projection queries)
    public static ProductDto ToDto(ProductData data) { ... }

    // 3. Domain → Data (persistence)
    public static ProductData ToData(Product product) { ... }

    // 4. Data → Domain (reconstruct from persistence)
    public static Product ToDomain(ProductData data) { ... }
}
```

### Symmetric Conversion (CRITICAL)

```csharp
// ✅ CORRECT - Symmetric: all fields both ways
public static ProductData ToData(Product product)
{
    return new ProductData
    {
        Id = product.Id.Value,
        Name = product.Name,
        Status = product.Status.ToString(),  // Serialize enum
        Tasks = JsonSerializer.Serialize(product.Tasks)  // Serialize complex
    };
}

public static Product ToDomain(ProductData data)
{
    return new Product(
        ProductId.From(data.Id),
        data.Name,
        Enum.Parse<ProductStatus>(data.Status),  // Deserialize enum
        JsonSerializer.Deserialize<List<Task>>(data.Tasks)  // Deserialize complex
    );
}

// ❌ WRONG - Asymmetric: field missing in ToDomain
public static Product ToDomain(ProductData data)
{
    return new Product(
        ProductId.From(data.Id),
        data.Name
        // Missing: Status, Tasks → DATA LOSS!
    );
}
```

### Mapper Checklist
- [ ] Located in `Application/<Aggregate>/Ports/`
- [ ] All methods `public static`
- [ ] No DI attributes
- [ ] Symmetric ToData/ToDomain
- [ ] Handles enum → string conversion
- [ ] Handles complex type JSON serialization

---

## Priority 2: Data Class (EF Core Entity)

**Location**: `src/Infrastructure/<Aggregate>/Persistence/` or `src/Application/<Aggregate>/Ports/Out/`

### Key Rules

| Check | Correct | Wrong |
|-------|---------|-------|
| Enum fields | Use `string` type | Use enum type |
| Complex types | JSON string + `[NotMapped]` | Direct navigation |
| Outbox fields | `[NotMapped]` attribute | Persisted |

### Correct Pattern

```csharp
public class ProductData
{
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;

    // ✅ CORRECT - Enum stored as string
    public string Status { get; set; } = string.Empty;

    // ✅ CORRECT - Complex type as JSON
    public string TasksJson { get; set; } = "[]";

    // ✅ CORRECT - Outbox fields not persisted
    [NotMapped]
    public List<DomainEventData> DomainEventDatas { get; set; } = new();

    [NotMapped]
    public string StreamName { get; set; } = string.Empty;

    // ✅ CORRECT - Optimistic concurrency
    public byte[] RowVersion { get; set; } = Array.Empty<byte>();
}
```

### Wrong Pattern

```csharp
public class ProductData
{
    // ❌ WRONG - Enum type (EF Core issues)
    public ProductStatus Status { get; set; }

    // ❌ WRONG - Missing [NotMapped] on Outbox fields
    public List<DomainEventData> DomainEventDatas { get; set; }

    // ❌ WRONG - No concurrency control
    // Missing RowVersion
}
```

### EF Core Fluent Configuration

```csharp
public class ProductDataConfiguration : IEntityTypeConfiguration<ProductData>
{
    public void Configure(EntityTypeBuilder<ProductData> builder)
    {
        builder.ToTable("products");
        builder.HasKey(x => x.Id);

        builder.Property(x => x.Name).IsRequired().HasMaxLength(200);
        builder.Property(x => x.Status).IsRequired().HasMaxLength(50);

        // ✅ CORRECT - Concurrency token
        builder.Property(x => x.RowVersion).IsRowVersion();

        // ✅ CORRECT - Ignore Outbox fields
        builder.Ignore(x => x.DomainEventDatas);
        builder.Ignore(x => x.StreamName);
    }
}
```

### Data Class Checklist
- [ ] No enum type fields (use string)
- [ ] Complex types stored as JSON string
- [ ] `[NotMapped]` on Outbox fields
- [ ] Has `RowVersion` for concurrency
- [ ] Has EF Core configuration class
- [ ] Table name is snake_case plural

---

## Priority 2: Repository Configuration

**Location**: `src/Infrastructure/Persistence/` or DI registration in `Program.cs`

### Key Rules

| Check | Correct | Wrong |
|-------|---------|-------|
| Interface | `IDomainRepository<TEntity, TId>` | Domain repository not aligned with shared contract |
| Methods | Match shared write contract | Added query-oriented methods |
| Queries | Via QueryService/QueryRepository | In Domain Repository |

### Correct Pattern

```csharp
// ✅ CORRECT - Shared write contract
public interface IDomainRepository<TEntity, in TId>
    where TEntity : IAggregateRoot<TId>
    where TId : notnull
{
    Task<TEntity?> FindByIdAsync(TId id, CancellationToken ct = default);
    Task<IEnumerable<TEntity>> FindByIdsAsync(IEnumerable<TId> ids, CancellationToken ct = default);
    Task SaveAsync(TEntity entity, CancellationToken ct = default);
    Task SaveAllAsync(IEnumerable<TEntity> entities, CancellationToken ct = default);
    Task DeleteAsync(TEntity entity, CancellationToken ct = default);
}

// ✅ CORRECT - DI registration
services.AddScoped<IDomainRepository<Product, Guid>, ProductDomainRepository>();
```

### Wrong Pattern

```csharp
// ❌ WRONG - Domain repository carries query methods
public interface IProductDomainRepository : IDomainRepository<Product, Guid>
{
    Task<Product?> FindByNameAsync(string name);  // FORBIDDEN!
    Task<IEnumerable<Product>> GetActiveProducts();  // FORBIDDEN!
}
```

### Repository Checklist
- [ ] Write side uses `IDomainRepository<TEntity, TId>`
- [ ] Domain wrapper (if any) does not add extra methods
- [ ] Write methods follow shared contract
- [ ] Complex queries use QueryService/QueryRepository
- [ ] Registered via DI, not attributes
- [ ] No empty inheritance classes

---

## Priority 3: Contract Tests

**Location**: `tests/Domain.Tests/<Aggregate>/Contracts/`

### Key Rules

| Check | Correct | Wrong |
|-------|---------|-------|
| Framework | Pure xUnit | NUnit, with Spring |
| Location | `Domain.Tests/.../Contracts/` | Mixed with Use Case tests |
| Pattern | `Assert.Throws<>` | Try-catch |

### Correct Pattern

```csharp
public class ProductContractTests
{
    [Fact]
    public void Rename_Throws_WhenNameIsNull()
    {
        // Arrange
        var product = CreateProductWithState(ProductStatus.Active);

        // Act & Assert
        Assert.Throws<ArgumentNullException>(() => product.Rename(null!));
    }

    [Fact]
    public void Rename_Throws_WhenNameIsEmpty()
    {
        var product = CreateProductWithState(ProductStatus.Active);

        Assert.Throws<ArgumentException>(() => product.Rename(string.Empty));
    }

    [Fact]
    public void Rename_Throws_WhenProductIsDeleted()
    {
        var product = CreateProductWithState(ProductStatus.Deleted);

        var ex = Assert.Throws<InvalidOperationException>(
            () => product.Rename("New Name"));
        Assert.Contains("deleted", ex.Message.ToLower());
    }

    private static Product CreateProductWithState(ProductStatus status)
    {
        var product = new Product(ProductId.Create(), "Test Product");
        // Set state via reflection or internal method for testing
        return product;
    }
}
```

### Wrong Pattern

```csharp
// ❌ WRONG - Using try-catch instead of Assert.Throws
[Fact]
public void Rename_Throws_WhenNameIsNull()
{
    try
    {
        product.Rename(null!);
        Assert.Fail("Expected exception");  // FORBIDDEN!
    }
    catch (ArgumentNullException) { }
}

// ❌ WRONG - Located in wrong folder
// tests/Application.Tests/ProductContractTests.cs

// ❌ WRONG - Mixed with integration tests
[Collection("IntegrationTests")]
public class ProductContractTests { }
```

### Contract Test Checklist
- [ ] File named `{Aggregate}ContractTests.cs`
- [ ] Located in `Domain.Tests/<Aggregate>/Contracts/`
- [ ] Pure xUnit (no integration test setup)
- [ ] Uses `Assert.Throws<TException>`
- [ ] Has `CreateProductWithState()` helper
- [ ] Each precondition has a test
- [ ] Clear test names describing the contract

---

## Quick Reference: Must Fail Conditions

If any of these are found, the review **MUST FAIL**:

### Domain Layer
1. (ES only) State set outside `When()` method in Aggregate Root
2. (ES only) Constructor sets state directly (not via `Apply(event)`)
3. Domain Event defined as `class` instead of `sealed record`
4. Domain Event missing `OccurredOn` timestamp
5. Entity not implementing `IEntity<TId>`
6. Value Object with setter methods

### Application Layer
7. `[Service]` or DI attributes on handlers
8. Domain write repository not aligned with `IDomainRepository<TEntity, TId>`
9. Repository with query methods (must use QueryService/QueryRepository)
10. Mapper with asymmetric ToData/ToDomain

### Infrastructure Layer
11. Enum type fields in Data Class (use string)
12. Missing `[NotMapped]` on Outbox fields
13. Missing `RowVersion` for concurrency
14. Empty repository inheritance class

### Test Layer
15. `BaseTestClass` usage (FORBIDDEN)
16. Tests not using BDDfy with Gherkin-style naming
17. Using Moq instead of NSubstitute
18. Contract tests in wrong location
19. Contract tests using try-catch instead of `Assert.Throws`

### General
20. `Console.WriteLine` or debug logging in production code
21. Comments in code (unless documentation)
22. Hardcoded connection strings or secrets

---

## Review Report Template

```markdown
## Code Review Report: [FileName]

### Test Status: [PASSING/FAILING]
- Command: `dotnet test --filter FullyQualifiedName~[TestClassName]`
- Result: [X tests passed / Y failed]

### Issues Summary
| Priority | Count | Status |
|----------|-------|--------|
| CRITICAL | X | [All Fixed / Y Remaining] |
| MUST FIX | X | [All Fixed / Y Remaining] |
| SHOULD FIX | X | [Documented] |

### Checklist Comparison
| Check Item | Result | Location | Issue Description |
|------------|--------|----------|-------------------|
| State only in When()? | ✅/❌ | line X | [Description] |
| Uses Apply(event)? | ✅/❌ | line Y | [Description] |
| ... | ... | ... | ... |

### Detailed Findings

#### CRITICAL Issues
1. **[Issue Title]** (line X-Y)
   - **Current**: `[problematic code]`
   - **Expected**: `[correct code]`
   - **Fix**: [Specific instruction]

#### MUST FIX Issues
1. **[Issue Title]** (line X)
   - **Issue**: [Description]
   - **Fix**: [Specific instruction]

#### SHOULD FIX Issues
1. **[Issue Title]** (line X)
   - **Suggestion**: [Description]

### Cross-Component Consistency (if Aggregate Review)
- [ ] Aggregate ID Value Object exists
- [ ] Domain Events use correct Aggregate ID
- [ ] Mapper has symmetric conversion
- [ ] Data Class matches Domain structure

### Rating: [1-5 stars] ⭐⭐⭐⭐⭐

### Verdict: [APPROVED / REJECTED / NEEDS REVISION]

### Next Steps
1. [Specific action item]
2. [Specific action item]
```

---

## Reference Files

- `.ai/CODE-REVIEW-INDEX.MD` - Quick index
- `.dev/standards/CODE-REVIEW-CHECKLIST.md` - Full checklist
- `.dev/standards/coding-standards/` - Detailed standards per component
- `.dev/adr/` - Architecture Decision Records

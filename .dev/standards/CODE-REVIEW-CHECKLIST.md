# Code Review Checklist (.NET)

> This checklist helps AI agents perform systematic code reviews and maintain consistent DDD, Clean Architecture, CQRS, and quality standards.

## 📋 Contents
1. [General Checks](#general-checks)
2. [Domain Layer Checks](#domain-layer-checks)
3. [UseCase Layer Checks](#usecase-layer-checks)
4. [Adapter Layer Checks](#adapter-layer-checks)
5. [Test Checks](#test-checks)
6. [Performance Checks](#performance-checks)
7. [Security Checks](#security-checks)
8. [Documentation Checks](#documentation-checks)

## ✅ General Checks

### 🚨 Avoid Overengineering (YAGNI)
- [ ] **MUST**: Implement only behavior explicitly required by the spec files.
- [ ] **MUST**: Keep Domain Events in one-to-one correspondence with the spec.
- [ ] **MUST**: Do not predict future requirements or implement features that might be useful later.
- [ ] **MUST**: Do not copy behavior solely because it appears in an example.

### Coding Conventions
- [ ] Follow C# naming conventions (PascalCase for classes and camelCase for methods).
- [ ] No unused `using` directives.
- [ ] No commented-out code.
- [ ] Use appropriate access modifiers.
- [ ] Follow the Single Responsibility Principle.

### Code Quality
- [ ] Methods do not exceed 30 lines; split longer methods.
- [ ] Classes do not exceed 300 lines.
- [ ] Cyclomatic complexity does not exceed 10.
- [ ] No duplicated code.

### Error Handling
- [ ] Exceptions are handled appropriately.
- [ ] Exceptions are not caught too broadly.
- [ ] Error messages are meaningful.
- [ ] Resources are released correctly (`using` / `await using`).

## 🏛️ Domain Layer Checks

### 🚨 Event Sourcing Compliance (Highest Priority)

#### 🔴 Constructor Responsibilities
- [ ] **CRITICAL**: Constructors must not set state fields directly, except for collection initialization.
- [ ] **CRITICAL**: Events must invoke `When(...)` through `Apply(event)`.
- [ ] **CRITICAL**: State assignment appears only in `When(...)` methods.

#### ✅ Correct Pattern
```csharp
public sealed class Product : AggregateRoot
{
    public Product(ProductId id, string name)
    {
        _tags = new List<Tag>();
        Apply(new ProductCreated(id.Value, name, DateProvider.Now()));
        Ensure("Product id set", () => _id.Value == id.Value);
    }

    private void When(ProductCreated e)
    {
        _id = new ProductId(e.ProductId);
        _name = e.Name;
    }
}
```

#### ❌ Anti-Pattern
```csharp
public Product(ProductId id, string name)
{
    _id = id; // ❌ Direct state assignment
    _name = name;
    AddDomainEvent(new ProductCreated(...)); // ❌ Apply is not used
}
```

### 🚨 Semantics Compliance
**Important**: Verify that `.dev/problem-frames/SEMANTICS.md` corresponds to `aggregate.yaml`.

#### value_immutable
- [ ] No setter.
- [ ] No mutation event.
- [ ] Values are assigned only in the creation event's `When` method.

#### identity
- [ ] Must also have `value_immutable`.
- [ ] No use case or event modifies the identity.

#### collection_reference_immutable
- [ ] The collection is initialized once and its reference cannot be replaced.
- [ ] Collection contents are modified only through Aggregate methods.

#### soft_delete_flag
- [ ] A corresponding Deleted event exists.
- [ ] Behavior is restricted after deletion.

#### optimistic_concurrency_version
- [ ] The version is managed by the framework.
- [ ] Manual modification is prohibited.

### Aggregate Package / Directory Organization
- [ ] Each Aggregate has an independent top-level folder and namespace.
- [ ] Aggregates reference one another only by ID.
- [ ] Value Objects are not defined more than once.

### Contract / Require / Reject / Ensure
- [ ] `Require` is used for preconditions.
- [ ] `Reject` is used only to avoid producing unnecessary events.
- [ ] `Ensure` is used for postconditions.

## 🧩 UseCase Layer Checks

### Use Case / Handler
- [ ] The Use Case interface is an explicit inbound port; implementations use the `*UseCase` suffix.
- [ ] Operations use `ExecuteAsync` with a required `CancellationToken`.
- [ ] Input/Output types do not reuse HTTP, MQ, or Wolverine/MediatR contracts.
- [ ] A Handler exists only for a real dispatch or message entry point.
- [ ] A Handler performs mapping and invokes one Use Case; it does not own orchestration.
- [ ] A Use Case does not depend directly on `IMessageBus` or another Use Case.
- [ ] It contains no Domain logic that belongs in an Aggregate.
- [ ] Constructor injection is used.
- [ ] Exceptions are wrapped in `UseCaseFailureException` when required by the standard.

### Command / Query Boundary
- [ ] Command / Query delivery contracts do not contain business execution logic.
- [ ] Command Use Cases handle state changes; Query Use Cases do not change domain state.
- [ ] Query Use Cases use a query repository or query service and do not route reads back through an Aggregate.
- [ ] A Controller may call a Query Repository/Service directly only for an explicitly approved pure-query exception.

### Repository / Domain Service Usage
- [ ] The command side loads and saves Aggregates through a repository.
- [ ] A Domain Service contains only Domain rules that genuinely cannot belong to a single Aggregate.
- [ ] Application orchestration is not misplaced in a Domain Service.

### Input/Output Design
- [ ] Input/Output types are independent records or classes.
- [ ] Input/Output types contain data fields only.
- [ ] DTOs are placed in `src/Contracts` or the directory required by the applicable standard.

### Spec Comparison
- [ ] Create a Spec comparison table.
- [ ] Remove implementation not required by the spec.
- [ ] The number of Domain Events matches the spec.

## 🔌 Adapter Layer Checks

### Controller
- [ ] The Controller contains no business logic.
- [ ] It does not access a Repository directly.
- [ ] It does not access an Aggregate directly.
- [ ] It only converts protocol input into a command/query and converts the result into a response.
- [ ] Using a bus or dispatcher within the same bounded context is a dispatch choice and is not mistaken for the Use Case itself.
- [ ] `ProblemDetails` provides a consistent error format.

### Mapper
- [ ] The Mapper belongs in the Application/Contracts layer.
- [ ] The Mapper is static or sealed; dependency injection is prohibited.
- [ ] Each DTO has one corresponding Mapper.

### Projection / Inquiry
- [ ] The interface is in Application and its implementation is in Infrastructure.
- [ ] Read models use EF Core Projection.
- [ ] No Domain behavior is mixed into the read model.

## 🧪 Test Checks

### BDD Rules
- [ ] All tests use GWT with Gherkin-style naming; 3A does not replace GWT.
- [ ] xUnit + BDDfy is the default. If the target team explicitly opts out of BDDfy, plain xUnit still preserves a Given / When / Then structure.
- [ ] `BaseTestClass` is prohibited.
- [ ] Mocks use NSubstitute.

### UseCase Test Given/When Rules
- [ ] Given/When steps interact only through the Use Case.
- [ ] Tests do not manipulate the Aggregate directly.

### Event Checks
- [ ] Events are verified through the MessageBus/Outbox.
- [ ] Tests do not inspect the Aggregate's internal event list directly.

### Coverage
- [ ] Use Cases have 100% coverage.
- [ ] Domain logic has 100% coverage.
- [ ] Error and boundary scenarios are tested.

## ⚡ Performance Checks
- [ ] Queries use Projection.
- [ ] N+1 queries are avoided.
- [ ] Batch operations are optimized.

## 🔒 Security Checks
- [ ] All input is validated.
- [ ] Injection and XSS are prevented.
- [ ] Sensitive information is not logged.
- [ ] API keys are not hard-coded.

## 📚 Documentation Checks
- [ ] README/Spec documentation is updated.
- [ ] New features are documented.
- [ ] Task files are updated when required by the workflow.

## 🔄 Projection Implementation Checks
- [ ] Create the Projection Interface.
- [ ] Create the EF Core Implementation.
- [ ] Use a Mapper to convert results.

## 🔗 Related Resources
- `coding-standards.md`
- `USECASE-COMMAND-HANDLER-RELATIONSHIP.MD`
- `../guides/implementation-guides/COMMON-MISTAKES-GUIDE.md`
- `../guides/implementation-guides/TEMPLATE-USAGE-GUIDE.md`

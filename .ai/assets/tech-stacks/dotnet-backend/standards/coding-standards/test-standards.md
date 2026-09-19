# Test Coding Standards (.NET)

Rule ID: `CONTRACT-SEMANTICS-001` applies when tests verify preconditions,
postconditions, or invariants.

This document defines coding standards for Domain, Use Case, Handler adapter, Controller, and integration tests.

---

## 📌 Overview

Rule IDs: `TEST-GWT-001`, `TEST-BDDFY-001`, `TEST-MOCK-001`.

All tests must express intent in Given-When-Then (GWT) style; Arrange-Act-Assert (3A) is not an acceptable substitute. xUnit + BDDfy is the default combination, with NSubstitute as the default mocking selection. A target team may explicitly opt out of BDDfy, but its C# tests must retain recognizable Given / When / Then structure and naming. A target may replace NSubstitute through the generic `testing.mocking` selection defined by [Target Technology Selection Policy](../../../../../../.dev/standards/TECHNOLOGY-SELECTION-POLICY.md).

- **xUnit**: Primary test framework
- **BDDfy**: Default GWT orchestration tool; a target team may explicitly opt out of the package but not the GWT rule
- **`.feature`**: Supported but optional; create and maintain these files only when requirements provide them directly, their design or production is explicitly requested, or the target profile adopts a Gherkin runner
- **NSubstitute**: Default mocking framework
- **Target override**: Another mocking library is permitted only through an explicit `testing.mocking` selection

---

## 🏷️ Pattern Markers (for Automated Checks)

The automated code-review scripts consume these markers:

```yaml
# Test framework rules
Pattern (forbidden, i): NUnit|MSTest|\[TestClass\]|\[TestMethod\]
Pattern (optional, any): BDDfy|TestStack\.BDDfy|Gherkin-style

# Mock rules
Pattern (optional, any): Substitute\.For

# Prohibit BaseTestClass
Pattern (forbidden, ignore-comment): BaseTestClass|BaseUseCaseTest
```

---

## 🔴 Mandatory Rules (MUST FOLLOW)

### 1. Test Framework Selection

| Test Type | Framework | Description |
|---------|------|------|
| Unit test | xUnit + BDDfy (default) | Must use GWT; opting out of BDDfy does not permit 3A |
| Integration test | xUnit + WebApplicationFactory | ASP.NET Core integration tests |
| Mocking | NSubstitute by default | Use the explicit target `testing.mocking` selection when present |
| Assertions | FluentAssertions | Recommended |

---

### 2. Do Not Use BaseTestClass

**Mandatory**: Test classes must be independent and must not inherit any test base class.

```csharp
// ❌ Incorrect: uses BaseTestClass
public class CreateProductUseCaseTests : BaseTestClass
{
    // FORBIDDEN!
}

// ❌ Incorrect: uses a shared base class
public class CreateProductUseCaseTests : IntegrationTestBase
{
    // FORBIDDEN!
}

// ✅ Correct: independent test class
public class CreateProductUseCaseTests
{
    private readonly IAggregateRepository<Product, ProductId> _repository;
    private readonly CreateProductUseCase _useCase;
    
    public CreateProductUseCaseTests()
    {
        _repository = Substitute.For<IAggregateRepository<Product, ProductId>>();
        _useCase = new CreateProductUseCase(_repository, ...);
    }
}
```

---

### 3. Use GWT; Default to BDDfy

**Mandatory**: All tests must use Given-When-Then semantics and recognizable step names. Arrange-Act-Assert (3A) must not replace GWT. Use Case and integration tests default to BDDfy; plain xUnit may implement the same GWT structure only when the target team explicitly opts out of that package.

`.feature` files and runners are not minimum dependencies. When requirements directly provide a `.feature` file, its design or production is explicitly requested, or the target profile has adopted a runner, create or maintain it according to the [Gherkin Feature Storage Guide](../../../../../../.dev/specs/tests/GHERKIN-FEATURE-STORAGE-GUIDE.MD). Otherwise, express the scenario directly as a GWT-style C# test.

#### Step Methods And Scenario Readability

For scenario-style unit, Use Case and integration tests, the test method must
read as Given/When/Then step calls, directly or through the selected fluent
runner. Give methods behavior-specific names such as `GivenMonthlyBudget`,
`WhenQueryingBudget` and `ThenAmountShouldBe`; comments or generic `Setup`,
`Execute` and `Check` methods alone do not satisfy this form. Preserve the
compact exception-contract form explicitly permitted in section 5; it still
needs an observable exception assertion and source traceability.

| Step | Responsibility | Must not substitute for |
| --- | --- | --- |
| Given | Establish the scenario's data/state and controlled dependency responses. Put reusable construction mechanics in helpers. | The primary action or the scenario's outcome assertions. Fixture guards may fail fast but are not Then coverage. |
| When | Execute the real subject's primary behavior once per scenario/data row and capture its result, state or exception. An intentional multi-operation behavior must be explicit in the design. | A mock of the subject, a fabricated result, or a hidden repeat of the action during verification. |
| Then / And | Assert each specified observable value, relation, state, event or exception against the result of that When. | Re-executing the subject, calculating the expected answer using its algorithm, or merely checking that no exception occurred when a value is specified. |

Keep material inputs and expected values visible in the scenario method or its
explicitly bound theory row. A business-named builder may encapsulate irrelevant
defaults; it must not hide the values that distinguish scenarios. Use fresh
per-test state, instance fixtures with isolated scenario state, or explicit
arguments/results. Avoid static mutable scenario fields and test-order coupling.
A result field must distinguish "not executed" from a legitimate default result
(for example, nullable captured data with a Then assertion that it is present).

For asynchronous behavior, await the step to completion using the selected
runner's supported Task API. Do not use `async void`, fire-and-forget actions,
`.Wait()` or `.Result`. Capture expected exceptions during When (for example
with xUnit `Record.ExceptionAsync`) and assert the required type and relevant
details during Then; do not swallow exceptions to make the test green. A bounded
eventual assertion may wait for an observable asynchronous outcome, but must not
repeat the command/query that caused it.

Use the [GWT handoff contract](../../../../shared/GWT-TEST-HANDOFF-CONTRACT.md)
to preserve scenario/data-row IDs, source/AC bindings and every Then-to-assertion
mapping. Parameterized cases are valid when each row remains identifiable and
uses the same behavior and assertion responsibilities. A generated report,
method-name match, successful build or passing run alone cannot prove that the
scenario was implemented faithfully.

#### Default BDDfy Form

This excerpt's fixture and step implementations are in the
[runnable step-method example](../../examples/bdd-step-methods/README.md).
It exposes the behavior-bearing data while keeping mechanics inside steps.

```csharp
[Fact]
public void Should_return_zero_when_query_month_has_no_budget()
{
    this.Given(x => x.GivenMonthlyBudget("202102", 28m))
        .When(x => x.WhenQueryingBudget(
            new DateOnly(2021, 1, 1), new DateOnly(2021, 1, 2)))
        .Then(x => x.ThenAmountShouldBe(0m))
        .BDDfy();
}
```

#### Explicit Plain-xUnit Opt-Out Form

The same example includes a separately selected BDDfy opt-out. Opting out of
the package preserves method responsibilities and GWT semantics.

```csharp
[Fact]
public async Task Should_return_zero_when_query_month_has_no_budget()
{
    GivenMonthlyBudget("202102", 28m);
    var actual = await WhenQueryingBudget(
        new DateOnly(2021, 1, 1), new DateOnly(2021, 1, 2));
    ThenAmountShouldBe(actual, 0m);
}
```

Test the concrete Use Case directly for business-flow behavior and mock its
outbound ports. Handler adapter tests remain separate and narrow: verify only
Command-to-Input mapping, exactly one Use Case invocation, and delivery-specific
failure mapping. A Handler test that mocks a Repository must not duplicate
responsibility for business-flow testing.

---

### 4. Test Data ID Rules

**Mandatory**: All aggregate-root IDs must use `Guid.NewGuid().ToString()` to avoid ID collisions between tests.

```csharp
// ✅ Correct: use Guid to generate a unique ID
private void GivenAValidCommand()
{
    _command = new CreateProductCommand(
        Guid.NewGuid().ToString(),  // ✅ Use Guid
        "Test Product",
        "user-123"  // userId may use a fixed string
    );
}

// ❌ Incorrect: uses a fixed ID
private void GivenAValidCommand()
{
    _command = new CreateProductCommand(
        "product-1",  // ❌ A fixed ID can cause duplicates
        "Test Product",
        "user-123"
    );
}
```

**Exception**: `userId` and `creatorId` may use fixed strings because they are not aggregate-root IDs.

---

### 5. Contract Tests for DBC Validation

**Mandatory**: Aggregate preconditions must have corresponding Contract Tests.

```csharp
// ✅ Correct: Contract Test using plain xUnit with explicit GWT sections
public class ProductContractTests
{
    [Fact]
    public void Rename_Throws_WhenNameIsNull()
    {
        // Given
        var product = CreateProductWithState(ProductState.Active);
        
        // When / Then
        Assert.Throws<ArgumentNullException>(() => product.Rename(null!));
    }
    
    [Fact]
    public void Rename_Throws_WhenProductIsDeleted()
    {
        // Given
        var product = CreateProductWithState(ProductState.Deleted);
        
        // When / Then
        var ex = Assert.Throws<InvalidOperationException>(
            () => product.Rename("New Name"));
        Assert.Contains("deleted", ex.Message.ToLower());
    }
    
    private static Product CreateProductWithState(ProductState state)
    {
        var product = new Product(ProductId.Create(), "Test");
        // Set state through an internal method or reflection
        return product;
    }
}

// ❌ Incorrect: uses try-catch
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
```

---

### 6. Mocking Library Selection

NSubstitute is the `TEST-MOCK-001` profile default. Before generating or
reviewing mocks, resolve `testing.mocking` through
`.dev/project-config.yaml#technologySelections` and
[Target Technology Selection Policy](../../../../../../.dev/standards/TECHNOLOGY-SELECTION-POLICY.md).

- When no target selection exists, use NSubstitute.
- When an evidenced target selection exists, use that library consistently.
- Do not mix mocking libraries without an explicit migration decision.
- Changing the library does not change GWT, test independence, or boundary
  interaction rules.

```csharp
// ✅ Correct: NSubstitute
var repository = Substitute.For<IAggregateRepository<Product, ProductId>>();
repository.FindByIdAsync(Arg.Any<ProductId>(), Arg.Any<CancellationToken>())
    .Returns(Task.FromResult<Product?>(existingProduct));

// Verify the call
await repository.Received(1).SaveAsync(Arg.Any<Product>(), Arg.Any<CancellationToken>());

// Valid only when the target explicitly selects Moq
var repository = new Mock<IAggregateRepository<Product, ProductId>>();
repository.Setup(x => x.FindByIdAsync(...)).ReturnsAsync(existingProduct);
repository.Verify(x => x.SaveAsync(...), Times.Once);
```

---

### 7. Isolate Event Mapping and Test Initialization

When tests depend on global event mapping, bootstrap, or domain-event mapper registration:

- Use a single bootstrap initialization path
- Initialize defensively within each test
- Do not allow tests to overwrite one another's global mapping state

```csharp
public static class TestBootstrap
{
    [ModuleInitializer]
    public static void Init()
    {
        BootstrapConfig.Initialize();
    }
}
```

```csharp
public class OutboxIntegrationTests
{
    public OutboxIntegrationTests()
    {
        BootstrapConfig.Initialize();
    }
}
```

When event names use a mapping prefix:

- The prefix must be consistent
- Different tests must not overwrite the same mapper with different naming strategies

This rule primarily prevents:

- Global-state contamination
- Test-order dependencies
- Interference between parallel tests

---

## 🎯 Test Layering Strategy

### Test Pyramid

```
         /\
        /E2E\      <- Fewest (5%)
       /------\
      /Integration\ <- Moderate (20%)
     /----------\
    / Controller \  <- More (25%)
   /--------------\
  /   Use Case    \ <- Many (25%)
 /------------------\
/    Unit Tests      \ <- Most (25%)
----------------------
```

### Responsibilities by Test Layer

| Layer | Scope | Framework | Mock Strategy |
|------|---------|---------|---------
| Unit Test | Domain logic, Value Objects | xUnit | No mocks |
| Use Case Test | Business flow | xUnit + BDDfy | Mock outbound ports |
| Handler Adapter Test | Input/failure mapping | xUnit | Mock one Use Case |
| Controller Test | HTTP behavior | WebApplicationFactory | Mock Use Case |
| Integration Test | Database, External API | xUnit | Real dependencies |
| E2E Test | Complete user journey | Playwright | No mocks |

---

## 🎯 Test Naming Rules

### Naming Pattern

```csharp
// Pattern: Should_[expected_result]_when_[condition]

// ✅ Good names
Should_create_product_successfully_when_input_is_valid()
Should_throw_exception_when_name_is_null()
Should_return_404_when_product_not_found()

// ❌ Poor names
TestCreateProduct()  // Too vague
Test1()              // Meaningless
CreateProductTest()  // Does not describe the expected result
```

### BDDfy Step Naming

```csharp
// ✅ Good step names
private void GivenAValidProductCreationInput() { }
private void GivenAnExistingProduct() { }
private async Task WhenTheUseCaseIsExecuted() { }
private void ThenTheProductShouldBeCreated() { }
private void ThenTheResultShouldBeSuccess() { }

// ❌ Poor step names
private void Setup() { }
private void DoTest() { }
private void Check() { }
```

---

## 🎯 Test Data Construction

### Test Data Builder Pattern

```csharp
public class ProductBuilder
{
    private ProductId _id = ProductId.Create();
    private string _name = "Default Product";
    private string _creatorId = "user-123";
    private ProductState _state = ProductState.Active;

    public static ProductBuilder AProduct() => new();

    public ProductBuilder WithId(ProductId id)
    {
        _id = id;
        return this;
    }

    public ProductBuilder WithName(string name)
    {
        _name = name;
        return this;
    }

    public ProductBuilder WithState(ProductState state)
    {
        _state = state;
        return this;
    }

    public Product Build()
    {
        var product = new Product(_id, _name, _creatorId);
        // Set state if needed
        return product;
    }
}

// Usage
var product = ProductBuilder.AProduct()
    .WithName("Custom Product")
    .WithState(ProductState.Deleted)
    .Build();
```

---

## 🔍 Checklist

### Use Case Tests
- [ ] Uses GWT and Gherkin-style naming; does not substitute 3A
- [ ] Uses BDDfy by default; when the target team explicitly opts out, plain xUnit still retains Given / When / Then structure
- [ ] Uses the resolved `testing.mocking` selection; defaults to NSubstitute
- [ ] Does not mix mocking libraries without an explicit migration decision
- [ ] Does not inherit BaseTestClass
- [ ] Uses `Guid.NewGuid().ToString()` for aggregate-root IDs
- [ ] Follows the `Should_xxx_when_xxx` naming pattern
- [ ] Tests the concrete `*UseCase` directly and mocks outbound ports

### Handler Adapter Tests
- [ ] Mocks one Use Case interface
- [ ] Verifies only input mapping, a single invocation, and delivery failure mapping
- [ ] Does not replace the Use Case business-flow test with a Handler test

### Contract Tests
- [ ] Uses GWT style; plain xUnit is allowed, but 3A is not
- [ ] Uses `Assert.Throws<TException>()`
- [ ] Has a `CreateProductWithState()` helper
- [ ] Has a corresponding test for every precondition

### Controller Tests
- [ ] Uses WebApplicationFactory
- [ ] Mocks a Use Case interface rather than a Handler or Repository
- [ ] Verifies the HTTP status code
- [ ] Verifies the response body

### Integration / Mapping Tests
- [ ] Initializes global event mapping through a single bootstrap path
- [ ] Initializes defensively within the test
- [ ] Does not depend on mapper state left by a previous test

### Profile / Environment Tests
- [ ] The host, fixture, or test command selects the test profile
- [ ] Does not modify global environment variables inside the test class
- [ ] `TestInMemory` does not register EF Core / Npgsql
- [ ] `TestOutbox` has a complete persistence chain

---

## 📂 Code Examples

For more complete examples, see:

| Example | Path |
|------|------|
| Reqnroll/Gherkin reference | [../../examples/bdd-gherkin-example/](../../examples/bdd-gherkin-example/) |
| BDD Given-When-Then | [../../examples/bdd-given-when-then-example/](../../examples/bdd-given-when-then-example/) |

---

## Related Documents

- [aggregate-standards.md](aggregate-standards.md)
- [Design By Contract Semantics](../DESIGN-BY-CONTRACT.md)
- [usecase-standards.md](usecase-standards.md)
- [controller-standards.md](controller-standards.md)
- [profile-configuration-standards.md](profile-configuration-standards.md)
- [../../../../../../.dev/guides/design-guides/FRAMEWORK-API-INTEGRATION-GUIDE.md](../../../../../../.dev/guides/design-guides/FRAMEWORK-API-INTEGRATION-GUIDE.md)

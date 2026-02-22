# Test Data Preparation Guide (Dotnet)

## Purpose
This guide defines how to prepare complete test data for Query Use Case tests to ensure query results are accurate and complete.

## Core Principles

### 1. Completeness
All Query Use Case tests must prepare **complete business objects**, including required attributes and related data.

### 2. Realism
Test data should reflect real business scenarios. Build data by calling other Use Cases, not by directly manipulating aggregates.

### 3. Isolation
Each test must prepare its own data and must not rely on the execution order of other tests.

## Defining testDataSetup in specs

```json
{
  "query": "GetProduct",
  "testDataSetup": {
    "description": "Prepare complete Product test data",
    "steps": [
      {
        "order": 1,
        "useCase": "CreateProductUseCase",
        "description": "Create the base Product",
        "input": {
          "id": "product-123",
          "name": "AI Scrum Assistant",
          "userId": "user-456"
        }
      },
      {
        "order": 2,
        "useCase": "SetProductGoalUseCase",
        "description": "Set Product Goal",
        "input": {
          "productId": "product-123",
          "productGoalId": "goal-123",
          "name": "Deliver AI-powered Scrum tools",
          "description": "Build comprehensive AI assistant",
          "state": "ACTIVE"
        }
      },
      {
        "order": 3,
        "useCase": "DefineDefinitionOfDoneUseCase",
        "description": "Define Definition of Done",
        "input": {
          "productId": "product-123",
          "name": "Standard DoD",
          "criteria": [
            "Code reviewed",
            "Unit tests written and passing",
            "Documentation updated",
            "Deployed to staging"
          ],
          "note": "Team agreed definition"
        }
      }
    ],
    "note": "After setup, clear captured events from the setup phase."
  }
}
```

## Aggregate-specific Data Requirements

### Product test data
- Must include:
  - Product basics (id, name, state)
  - ProductGoal (via SetProductGoalUseCase)
  - DefinitionOfDone (via DefineDefinitionOfDoneUseCase)
  - Related ProductBacklogItems (if needed for query)

### Sprint test data
- Must include:
  - Sprint basics (id, name, state)
  - SprintGoal (via DefineSprintGoalUseCase)
  - Timebox settings (via SetSprintTimeboxUseCase)
  - Selected PBIs (via SelectProductBacklogItemUseCase)
  - Team members (if needed for query)

### ProductBacklogItem test data
- Must include:
  - PBI basics (id, name, description, state)
  - Estimates (via EstimateProductBacklogItemUseCase)
  - Tasks (via CreateTaskUseCase)
  - Sprint linkage (if already selected)
  - Priority/importance fields

## Test Template (xUnit + BDDfy)

```csharp
public sealed class GetProductQueryTests : IClassFixture<TestProfileFixture>
{
    private readonly TestProfileFixture _fixture;
    private GetProductOutput? _output;

    public GetProductQueryTests(TestProfileFixture fixture)
    {
        _fixture = fixture;
    }

    [Fact]
    public void Get_product_with_complete_data()
    {
        this.BDDfy();
    }

    async Task Given_a_complete_Product_exists()
    {
        var createProduct = _fixture.Services.GetRequiredService<ICreateProductUseCase>();
        var setGoal = _fixture.Services.GetRequiredService<ISetProductGoalUseCase>();
        var defineDod = _fixture.Services.GetRequiredService<IDefineDefinitionOfDoneUseCase>();

        await createProduct.Execute(CreateProductInput.Create("product-123", "AI Scrum Assistant", "user-456"));
        await setGoal.Execute(SetProductGoalInput.Create("product-123", "goal-123", "Deliver AI-powered Scrum tools"));
        await defineDod.Execute(DefineDefinitionOfDoneInput.Create("product-123", "Standard DoD"));

        // Wait for events from setup, then clear
        await _fixture.AwaitEvents(count: 3);
        _fixture.ClearEvents();
    }

    async Task When_I_query_the_product()
    {
        var getProduct = _fixture.Services.GetRequiredService<IGetProductUseCase>();
        _output = await getProduct.Execute(GetProductInput.Create("product-123"));
    }

    void Then_the_response_contains_full_Product_data()
    {
        _output.Should().NotBeNull();
        _output!.ExitCode.Should().Be(ExitCode.Success);
        _output.Product.Name.Should().Be("AI Scrum Assistant");
        _output.Product.DefinitionOfDone.Should().NotBeNull();
    }
}
```

## Fixture Support (replace BaseUseCaseTest)

```csharp
public sealed class TestProfileFixture
{
    public IServiceProvider Services { get; }
    public IReadOnlyList<DomainEvent> CapturedEvents => _eventListener.Events;

    public TestProfileFixture()
    {
        var services = new ServiceCollection();
        services.AddUseCases();
        services.AddInMemoryProfile();

        _eventListener = new FakeEventListener();
        services.AddSingleton(_eventListener);

        Services = services.BuildServiceProvider();
    }

    public Task AwaitEvents(int count)
    {
        // TODO: implement async-safe await for event capture
        return Task.CompletedTask;
    }

    public void ClearEvents() => _eventListener.Clear();
}
```

## InMemory Profile Test Isolation

### Critical: clear in-memory stores before each test
When using the InMemory profile, **clear repositories and message stores before each test** to avoid data leakage.

```csharp
public sealed class TestProfileFixture : IAsyncLifetime
{
    public Task InitializeAsync()
    {
        // TODO: clear InMemoryOrmDb and InMemoryMessageDb equivalents
        // _productOrmDb.Clear();
        // _sprintOrmDb.Clear();
        // _messageDb.Clear();
        ClearEvents();
        return Task.CompletedTask;
    }

    public Task DisposeAsync() => Task.CompletedTask;
}
```

Why this matters:
- In-memory stores persist across tests unless manually cleared
- `IClassFixture` does not reset per test method automatically
- Leaked data causes flaky tests

## Common Mistakes

### Mistake 1: Creating aggregates directly
Wrong:
```csharp
var product = new Product(...);
_repository.Save(product);
```

Correct:
```csharp
await _createProductUseCase.Execute(input);
```

### Mistake 2: Incomplete test data
Wrong:
```csharp
await _createProductUseCase.Execute(input);
// missing goal and DoD setup
```

### Mistake 3: Forgetting to clear setup events
Wrong:
```csharp
await _createProductUseCase.Execute(input);
await _setGoalUseCase.Execute(goalInput);
// missing clear
```

Correct:
```csharp
await _createProductUseCase.Execute(input);
await _setGoalUseCase.Execute(goalInput);
await _fixture.AwaitEvents(count: 2);
_fixture.ClearEvents();
```

## Checklist

Before running Query Use Case tests, confirm:
- [ ] All required Use Cases are called to prepare data
- [ ] Test data includes all required attributes
- [ ] Setup uses Use Cases, not direct aggregate manipulation
- [ ] Setup events are cleared after capture
- [ ] Then phase verifies all required fields
- [ ] Each test is independent and isolated

## References
- `.dev/guides/PROFILE-BASED-TESTING-GUIDE.md`
- `.ai/prompts/usecase-test-generation-prompt.md`
- `.ai/prompts/testing-standards-prompt.md`


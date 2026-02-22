# xUnit + BDDfy Example (Dotnet)

This example uses Gherkin-style naming inside test methods. No `.feature` files.

```csharp
public sealed class CreateProductUseCaseTests
{
    private readonly ICreateProductUseCase _useCase;
    private Result _result = Result.Fail();

    public CreateProductUseCaseTests(ICreateProductUseCase useCase)
    {
        _useCase = useCase;
    }

    [Fact]
    public void Create_product_successfully()
    {
        this.BDDfy();
    }

    void Given_a_valid_create_product_request()
    {
        // TODO: prepare input
    }

    void When_the_create_product_use_case_is_executed()
    {
        // TODO: execute use case and store result
    }

    void Then_the_result_should_be_success()
    {
        // TODO: assert result
    }

    void And_a_ProductCreated_event_should_be_published()
    {
        // TODO: assert event publication
    }
}
```

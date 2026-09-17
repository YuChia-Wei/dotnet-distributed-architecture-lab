using NSubstitute;
using TestStack.BDDfy;
using Xunit;

namespace GwtStepMethods.DefaultBddfy;

public sealed class BudgetQueryTests
{
    private readonly IBudgetRepository _repository = Substitute.For<IBudgetRepository>();
    private readonly BudgetQuery _subject;
    private decimal? _actual;
    private Exception? _exception;

    public BudgetQueryTests() => _subject = new BudgetQuery(_repository);

    [Fact]
    [Trait("Scenario", "BUDGET-01")]
    public void Should_return_zero_when_query_month_has_no_budget()
    {
        this.Given(x => x.GivenMonthlyBudget("202102", 28m))
            .When(x => x.WhenQueryingBudget(
                new DateOnly(2021, 1, 1), new DateOnly(2021, 1, 2)))
            .Then(x => x.ThenAmountShouldBe(0m))
            .BDDfy();
    }

    [Theory]
    [InlineData("BUDGET-02/integer", 300, 2, 20)]
    [InlineData("BUDGET-02/fractional", 45, 3, 4.5)]
    [Trait("Scenario", "BUDGET-02")]
    public void Should_prorate_the_inclusive_range(
        string scenarioRow, decimal monthlyAmount, int lastDay, decimal expected)
    {
        this.Given(x => x.GivenMonthlyBudget("202104", monthlyAmount))
            .When(x => x.WhenQueryingBudget(
                new DateOnly(2021, 4, 1), new DateOnly(2021, 4, lastDay)))
            .Then(x => x.ThenAmountShouldBe(expected))
            .BDDfy(scenarioRow);
    }

    [Fact]
    [Trait("Scenario", "BUDGET-03")]
    public void Should_sum_both_months_when_the_range_crosses_a_month_boundary()
    {
        this.Given(x => x.GivenBudgets(
                new MonthlyBudget("202101", 310m), new MonthlyBudget("202102", 280m)))
            .When(x => x.WhenQueryingBudget(
                new DateOnly(2021, 1, 31), new DateOnly(2021, 2, 1)))
            .Then(x => x.ThenAmountShouldBe(20m))
            .BDDfy();
    }

    [Fact]
    [Trait("Scenario", "BUDGET-04")]
    public void Should_reject_an_inverted_range_before_reading_budgets()
    {
        this.Given(x => x.GivenMonthlyBudget("202104", 300m))
            .When(x => x.WhenQueryingAnInvalidRange(
                new DateOnly(2021, 4, 2), new DateOnly(2021, 4, 1)))
            .Then(x => x.ThenTheRangeShouldBeRejected("end"))
            .And(x => x.ThenTheRepositoryShouldNotBeRead())
            .BDDfy();
    }

    private void GivenMonthlyBudget(string month, decimal amount) =>
        GivenBudgets(new MonthlyBudget(month, amount));

    private void GivenBudgets(params MonthlyBudget[] budgets) =>
        _repository.GetAllAsync(Arg.Any<CancellationToken>())
            .Returns(Task.FromResult<IReadOnlyList<MonthlyBudget>>(budgets));

    private async Task WhenQueryingBudget(DateOnly start, DateOnly end) =>
        _actual = await _subject.QueryAsync(start, end);

    private async Task WhenQueryingAnInvalidRange(DateOnly start, DateOnly end) =>
        _exception = await Record.ExceptionAsync(() => _subject.QueryAsync(start, end));

    private void ThenAmountShouldBe(decimal expected)
    {
        Assert.True(_actual.HasValue, "When must capture an actual result, including zero.");
        Assert.Equal(expected, _actual.Value);
    }

    private void ThenTheRangeShouldBeRejected(string parameterName)
    {
        var error = Assert.IsType<ArgumentException>(_exception);
        Assert.Equal(parameterName, error.ParamName);
    }

    private async Task ThenTheRepositoryShouldNotBeRead() =>
        await _repository.DidNotReceive().GetAllAsync(Arg.Any<CancellationToken>());
}

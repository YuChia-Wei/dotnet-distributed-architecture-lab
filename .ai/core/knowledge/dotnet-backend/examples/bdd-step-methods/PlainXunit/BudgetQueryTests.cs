using NSubstitute;
using Xunit;

namespace GwtStepMethods.PlainXunit;

// This example's explicit BDDfy opt-out is recorded in scenarios.md.
public sealed class BudgetQueryTests
{
    private readonly IBudgetRepository _repository = Substitute.For<IBudgetRepository>();
    private readonly BudgetQuery _subject;

    public BudgetQueryTests() => _subject = new BudgetQuery(_repository);

    [Fact]
    [Trait("Scenario", "BUDGET-01")]
    public async Task Should_return_zero_when_query_month_has_no_budget()
    {
        GivenMonthlyBudget("202102", 28m);
        var actual = await WhenQueryingBudget(
            new DateOnly(2021, 1, 1), new DateOnly(2021, 1, 2));
        ThenAmountShouldBe(actual, 0m);
    }

    [Theory]
    [InlineData("BUDGET-02/integer", 300, 2, 20)]
    [InlineData("BUDGET-02/fractional", 45, 3, 4.5)]
    [Trait("Scenario", "BUDGET-02")]
    public async Task Should_prorate_the_inclusive_range(
        string scenarioRow, decimal monthlyAmount, int lastDay, decimal expected)
    {
        GivenMonthlyBudget("202104", monthlyAmount);
        var actual = await WhenQueryingBudget(
            new DateOnly(2021, 4, 1), new DateOnly(2021, 4, lastDay));
        ThenAmountShouldBe(actual, expected, scenarioRow);
    }

    [Fact]
    [Trait("Scenario", "BUDGET-03")]
    public async Task Should_sum_both_months_when_the_range_crosses_a_month_boundary()
    {
        GivenBudgets(new MonthlyBudget("202101", 310m), new MonthlyBudget("202102", 280m));
        var actual = await WhenQueryingBudget(
            new DateOnly(2021, 1, 31), new DateOnly(2021, 2, 1));
        ThenAmountShouldBe(actual, 20m);
    }

    [Fact]
    [Trait("Scenario", "BUDGET-04")]
    public async Task Should_reject_an_inverted_range_before_reading_budgets()
    {
        GivenMonthlyBudget("202104", 300m);
        var error = await WhenQueryingAnInvalidRange(
            new DateOnly(2021, 4, 2), new DateOnly(2021, 4, 1));
        ThenTheRangeShouldBeRejected(error, "end");
        await ThenTheRepositoryShouldNotBeRead();
    }

    private void GivenMonthlyBudget(string month, decimal amount) =>
        GivenBudgets(new MonthlyBudget(month, amount));

    private void GivenBudgets(params MonthlyBudget[] budgets) =>
        _repository.GetAllAsync(Arg.Any<CancellationToken>())
            .Returns(Task.FromResult<IReadOnlyList<MonthlyBudget>>(budgets));

    private Task<decimal> WhenQueryingBudget(DateOnly start, DateOnly end) =>
        _subject.QueryAsync(start, end);

    private async Task<Exception?> WhenQueryingAnInvalidRange(DateOnly start, DateOnly end) =>
        await Record.ExceptionAsync(() => _subject.QueryAsync(start, end));

    private static void ThenAmountShouldBe(decimal actual, decimal expected, string? scenarioRow = null)
    {
        Assert.True(actual == expected, $"{scenarioRow ?? "Amount"}: expected {expected}, actual {actual}.");
    }

    private static void ThenTheRangeShouldBeRejected(Exception? exception, string parameterName)
    {
        var error = Assert.IsType<ArgumentException>(exception);
        Assert.Equal(parameterName, error.ParamName);
    }

    private async Task ThenTheRepositoryShouldNotBeRead() =>
        await _repository.DidNotReceive().GetAllAsync(Arg.Any<CancellationToken>());
}

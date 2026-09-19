using System.Globalization;

namespace GwtStepMethods;

// Original, deliberately bounded example subject. See scenarios.md for its
// complete fixture contract; this is not a production budgeting component.
public sealed record MonthlyBudget(string YearMonth, decimal Amount);

public interface IBudgetRepository
{
    Task<IReadOnlyList<MonthlyBudget>> GetAllAsync(CancellationToken cancellationToken);
}

public sealed class BudgetQuery(IBudgetRepository repository)
{
    public async Task<decimal> QueryAsync(
        DateOnly start, DateOnly end, CancellationToken cancellationToken = default)
    {
        if (end < start)
            throw new ArgumentException("End must not precede start.", nameof(end));

        var budgets = await repository.GetAllAsync(cancellationToken);
        decimal total = 0;
        var day = start;
        while (true)
        {
            var month = day.ToString("yyyyMM", CultureInfo.InvariantCulture);
            var amount = budgets.SingleOrDefault(b => b.YearMonth == month)?.Amount ?? 0m;
            total += amount / DateTime.DaysInMonth(day.Year, day.Month);
            if (day == end)
                return total;
            day = day.AddDays(1);
        }
    }
}

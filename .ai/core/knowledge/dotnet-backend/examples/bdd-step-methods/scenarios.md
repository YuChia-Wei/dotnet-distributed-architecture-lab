# Budget Query Example Contract

Source identity: `GWT-BUDGET-EXAMPLE/v1`, owned by this example. Scenario IDs
below are local example identities, not downstream requirement IDs. The source
revision is the Git revision of this file used by an execution. These are
approved fixture expectations, not reverse-engineered product requirements.

The real subject is `BudgetQuery.QueryAsync`. It reads an asynchronous outbound
repository port, divides each supplied monthly budget by that calendar month's
day count using decimal arithmetic, and totals both inclusive range endpoints.
A missing month contributes zero. An inverted range throws `ArgumentException`
with parameter name `end`, before reading the repository. Inputs contain at most
one record per month. Currency rounding, malformed month keys, duplicate budget
records, cancellation policy and production-scale ranges are outside this
teaching fixture's contract; do not infer their business rules.

## Selected Technology And Test Level

- Test level: isolated use-case unit tests; construct the real `BudgetQuery` and
  substitute only `IBudgetRepository`. No database, broker, host or DI fixture.
- `DefaultBddfy`: the framework's xUnit + BDDfy default.
- `PlainXunit`: an explicit example-owned opt-out of BDDfy to demonstrate the
  permitted method-based GWT equivalent. It does not change the default for
  another target or make opt-out implicit.
- Both select NSubstitute and share the same subject, scenarios and expectations.
- Pinned package versions in the project files make this example reproducible;
  they are not a framework-wide package-version policy.

## Scenarios

| Scenario / row | Given | When | Then / And |
| --- | --- | --- | --- |
| BUDGET-01 | Only February 2021 has a budget of 28 | Query 2021-01-01 through 2021-01-02 | Amount is exactly 0 |
| BUDGET-02/integer | April 2021 budget is 300 | Query 2021-04-01 through 2021-04-02 | Amount is exactly 20 |
| BUDGET-02/fractional | April 2021 budget is 45 | Query 2021-04-01 through 2021-04-03 | Amount is exactly 4.5 |
| BUDGET-03 | January 2021 budget is 310 and February is 280 | Query 2021-01-31 through 2021-02-01 | Amount is exactly 20 |
| BUDGET-04 | April 2021 budget is 300 | Query 2021-04-02 through 2021-04-01 | Exact exception type is ArgumentException; parameter is end; repository is not read |

Expected values above are fixed examples of this contract. They remain explicit
in the test body or theory row; tests do not recompute the budget algorithm to
obtain them. The two BUDGET-02 rows intentionally share one theory because their
setup/action/assertion responsibilities match. Their distinct IDs appear in
test results. Every test instance starts with a new subject and substitute.

## Implementation Mapping

The following mapping applies independently to
`DefaultBddfy/BudgetQueryTests.cs` and `PlainXunit/BudgetQueryTests.cs`, whose test
classes have the corresponding `GwtStepMethods.DefaultBddfy` and
`GwtStepMethods.PlainXunit` namespaces.

| Scenario / row | Test method | Given | When | Outcome assertions |
| --- | --- | --- | --- | --- |
| BUDGET-01 | Should_return_zero_when_query_month_has_no_budget | GivenMonthlyBudget | WhenQueryingBudget | ThenAmountShouldBe checks exact amount |
| BUDGET-02/integer; BUDGET-02/fractional | Should_prorate_the_inclusive_range, identified by scenarioRow | GivenMonthlyBudget | WhenQueryingBudget | ThenAmountShouldBe checks each row's exact amount |
| BUDGET-03 | Should_sum_both_months_when_the_range_crosses_a_month_boundary | GivenBudgets | WhenQueryingBudget | ThenAmountShouldBe checks exact amount |
| BUDGET-04 | Should_reject_an_inverted_range_before_reading_budgets | GivenMonthlyBudget | WhenQueryingAnInvalidRange | ThenTheRangeShouldBeRejected asserts exact type and parameter; ThenTheRepositoryShouldNotBeRead asserts zero reads |

BDDfy awaits Task-returning steps through its selected runner. The plain profile
awaits the returned action/exception directly. No Then repeats the query. The
BDDfy result is nullable so an omitted When cannot satisfy the zero-amount case
from a field initializer alone. Plain xUnit passes the actual result explicitly.

Execution status is supplied by the command's actual output and result files,
not this static mapping. The example expects five discovered, passed cases in
each profile, including both theory rows; skipped, absent or zero-discovery
results do not satisfy that expectation.

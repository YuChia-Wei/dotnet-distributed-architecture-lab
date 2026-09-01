using Shouldly;
using Wolverine;
using InventoryConsumerFailurePolicy = InventoryControl.Consumer.Messaging.ConsumerFailurePolicy;
using OrdersConsumerFailurePolicy = SaleOrders.Consumer.Messaging.ConsumerFailurePolicy;
using ProductsConsumerFailurePolicy = SaleProducts.Consumer.Messaging.ConsumerFailurePolicy;

namespace SaleProducts.Tests;

public sealed class ConsumerFailurePolicyTests
{
    [Fact]
    public void given_the_products_consumer_policy_when_configured_then_retries_are_bounded_before_dead_lettering()
    {
        then_retries_are_bounded_before_dead_lettering(
            ProductsConsumerFailurePolicy.Configure,
            ProductsConsumerFailurePolicy.TransientRetryDelays,
            ProductsConsumerFailurePolicy.UnhandledExceptionRetryCount);
    }

    [Fact]
    public void given_the_orders_consumer_policy_when_configured_then_retries_are_bounded_before_dead_lettering()
    {
        then_retries_are_bounded_before_dead_lettering(
            OrdersConsumerFailurePolicy.Configure,
            OrdersConsumerFailurePolicy.TransientRetryDelays,
            OrdersConsumerFailurePolicy.UnhandledExceptionRetryCount);
    }

    [Fact]
    public void given_the_inventory_consumer_policy_when_configured_then_retries_are_bounded_before_dead_lettering()
    {
        then_retries_are_bounded_before_dead_lettering(
            InventoryConsumerFailurePolicy.Configure,
            InventoryConsumerFailurePolicy.TransientRetryDelays,
            InventoryConsumerFailurePolicy.UnhandledExceptionRetryCount);
    }

    private static void then_retries_are_bounded_before_dead_lettering(
        Action<WolverineOptions> configure,
        IReadOnlyList<TimeSpan> transientRetryDelays,
        int unhandledExceptionRetryCount)
    {
        var options = new WolverineOptions();
        var existingRuleCount = options.Policies.Failures.Count();

        Should.NotThrow(() => configure(options));

        transientRetryDelays.ShouldBe(
        [
            TimeSpan.FromMilliseconds(100),
            TimeSpan.FromMilliseconds(500),
            TimeSpan.FromSeconds(2)
        ]);
        unhandledExceptionRetryCount.ShouldBe(1);

        var configuredRules = options.Policies.Failures.Skip(existingRuleCount).ToArray();
        configuredRules.Length.ShouldBe(2);
        configuredRules[0].Count().ShouldBe(4);
        configuredRules[1].Count().ShouldBe(2);
        configuredRules[0].Take(3).ShouldAllBe(
            slot => slot.Describe().Contains("retry", StringComparison.OrdinalIgnoreCase));
        configuredRules[1].Take(1).ShouldAllBe(
            slot => slot.Describe().Contains("retry", StringComparison.OrdinalIgnoreCase));
        configuredRules[0].Last().Describe().ShouldContain("error", Case.Insensitive);
        configuredRules[1].Last().Describe().ShouldContain("error", Case.Insensitive);
    }
}

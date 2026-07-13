using SaleOrders.Domains.DomainEvents;
using Shouldly;

namespace SaleOrders.Domains.Tests;

public class OrderTests
{
    private const string Reason = "operator confirmed the lifecycle change";

    [Theory]
    [InlineData(OrderStatus.Cancelled)]
    [InlineData(OrderStatus.Shipped)]
    [InlineData(OrderStatus.Delivered)]
    public void Given_a_placed_order_when_state_changes_then_reason_is_recorded(OrderStatus targetStatus)
    {
        var order = CreateOrder();

        var changed = ChangeState(order, targetStatus, Reason);

        changed.ShouldBeTrue();
        order.Status.ShouldBe(targetStatus);
        var transitionEvent = order.DomainEvents.Last();
        GetReason(transitionEvent).ShouldBe(Reason);
    }

    [Theory]
    [InlineData(OrderStatus.Cancelled)]
    [InlineData(OrderStatus.Shipped)]
    [InlineData(OrderStatus.Delivered)]
    public void Given_a_target_state_when_same_transition_repeats_then_it_is_a_no_op(OrderStatus targetStatus)
    {
        var order = CreateOrder();
        ChangeState(order, targetStatus, Reason);
        var eventCount = order.DomainEvents.Count;

        var changed = ChangeState(order, targetStatus, "duplicate request");

        changed.ShouldBeFalse();
        order.Status.ShouldBe(targetStatus);
        order.DomainEvents.Count.ShouldBe(eventCount);
    }

    [Theory]
    [InlineData(OrderStatus.Cancelled, null)]
    [InlineData(OrderStatus.Shipped, "")]
    [InlineData(OrderStatus.Delivered, "   ")]
    public void Given_a_missing_reason_when_state_change_is_requested_then_the_order_is_unchanged(
        OrderStatus targetStatus,
        string? reason)
    {
        var order = CreateOrder();
        var eventCount = order.DomainEvents.Count;

        Should.Throw<ArgumentException>(() => ChangeState(order, targetStatus, reason!));

        order.Status.ShouldBe(OrderStatus.Placed);
        order.DomainEvents.Count.ShouldBe(eventCount);
    }

    [Fact]
    public void Given_event_history_when_order_is_rehydrated_then_only_history_defines_state()
    {
        var orderId = Guid.CreateVersion7();
        var productId = Guid.CreateVersion7();
        var events = new Lab.BuildingBlocks.Domains.IDomainEvent[]
        {
            new OrderPlacedDomainEvent(orderId, DateTime.UtcNow, 100m, productId, "Product", 1, DateTime.UtcNow),
            new OrderCancelledDomainEvent(orderId, "customer request", DateTime.UtcNow),
            new OrderShippedDomainEvent(orderId, "manual override", DateTime.UtcNow)
        };

        var order = new Order(events);

        order.Id.ShouldBe(orderId);
        order.Status.ShouldBe(OrderStatus.Shipped);
        order.Version.ShouldBe(events.Length);
        order.DomainEvents.ShouldBeEmpty();
    }

    [Fact]
    public void Given_pending_events_when_commit_is_confirmed_then_version_advances_and_events_clear()
    {
        var order = CreateOrder();

        order.MarkChangesAsCommitted(1);

        order.Version.ShouldBe(1);
        order.DomainEvents.ShouldBeEmpty();
    }

    [Fact]
    public void Given_pending_events_when_commit_version_is_inconsistent_then_state_is_preserved()
    {
        var order = CreateOrder();

        Should.Throw<InvalidOperationException>(() => order.MarkChangesAsCommitted(2));

        order.Version.ShouldBe(0);
        order.DomainEvents.Count.ShouldBe(1);
    }

    private static Order CreateOrder()
        => new(DateTime.UtcNow, 100m, Guid.CreateVersion7(), "Product", 1);

    private static bool ChangeState(Order order, OrderStatus targetStatus, string reason)
        => targetStatus switch
        {
            OrderStatus.Cancelled => order.Cancel(reason),
            OrderStatus.Shipped => order.Ship(reason),
            OrderStatus.Delivered => order.Deliver(reason),
            _ => throw new ArgumentOutOfRangeException(nameof(targetStatus), targetStatus, null)
        };

    private static string GetReason(Lab.BuildingBlocks.Domains.IDomainEvent @event)
        => @event switch
        {
            OrderCancelledDomainEvent cancelled => cancelled.Reason,
            OrderShippedDomainEvent shipped => shipped.Reason,
            OrderDeliveredDomainEvent delivered => delivered.Reason,
            _ => throw new InvalidOperationException($"Unexpected event type {@event.GetType().Name}.")
        };
}

using BuildingBlocks.Domain;
using Xunit;

namespace DotnetBackendBuildingBlocks.Tests;

public sealed class EsAggregateRootTests
{
    [Fact]
    public void Given_committed_history_when_replayed_then_state_and_version_are_restored_without_pending_events()
    {
        var aggregate = CounterAggregate.FromHistory(
            new CounterChanged(2),
            new CounterChanged(3));

        Assert.Equal(5, aggregate.Value);
        Assert.Equal(2, aggregate.Version);
        Assert.Empty(aggregate.DomainEvents);
    }

    [Fact]
    public void Given_a_new_event_when_applied_then_when_dispatches_and_event_remains_pending()
    {
        var aggregate = new CounterAggregate("counter-1");

        aggregate.ChangeBy(4);

        Assert.Equal(4, aggregate.Value);
        Assert.Equal(0, aggregate.Version);
        Assert.IsType<CounterChanged>(Assert.Single(aggregate.DomainEvents));
        Assert.IsType<CounterChanged>(aggregate.LastPendingEvent);
    }

    [Fact]
    public void Given_pending_events_when_commit_is_confirmed_then_version_advances_and_pending_events_clear()
    {
        var aggregate = CounterAggregate.FromHistory(new CounterChanged(2));
        aggregate.ChangeBy(3);
        aggregate.ChangeBy(4);

        aggregate.MarkChangesAsCommitted(3);

        Assert.Equal(9, aggregate.Value);
        Assert.Equal(3, aggregate.Version);
        Assert.Empty(aggregate.DomainEvents);
    }

    [Fact]
    public void Given_an_unexpected_committed_version_when_confirmed_then_state_is_left_for_retry()
    {
        var aggregate = CounterAggregate.FromHistory(new CounterChanged(2));
        aggregate.ChangeBy(3);

        var exception = Assert.Throws<InvalidOperationException>(
            () => aggregate.MarkChangesAsCommitted(99));

        Assert.Contains("expected version 2", exception.Message);
        Assert.Equal(1, aggregate.Version);
        Assert.Single(aggregate.DomainEvents);
        Assert.Equal(5, aggregate.Value);
    }

    [Fact]
    public void Given_an_initialized_aggregate_when_history_is_replayed_again_then_replay_is_rejected()
    {
        var aggregate = CounterAggregate.FromHistory(new CounterChanged(2));

        Assert.Throws<InvalidOperationException>(
            () => aggregate.ReplayAgain(new CounterChanged(3)));
    }

    private sealed class CounterAggregate : EsAggregateRoot<string>
    {
        private string _id = "unset";

        public CounterAggregate(string id)
        {
            _id = id;
        }

        private CounterAggregate(IEnumerable<IDomainEvent> history)
        {
            Replay(history);
        }

        public override string Id => _id;

        public int Value { get; private set; }

        public IDomainEvent? LastPendingEvent => LastDomainEvent;

        public static CounterAggregate FromHistory(params IDomainEvent[] history) =>
            new(history);

        public void ChangeBy(int delta) => Apply(new CounterChanged(delta));

        public void ReplayAgain(IDomainEvent @event) => Replay([@event]);

        protected override void When(IDomainEvent @event)
        {
            switch (@event)
            {
                case CounterChanged changed:
                    Value += changed.Delta;
                    break;
                default:
                    throw new InvalidOperationException(
                        $"Unsupported event type '{@event.GetType().Name}'.");
            }
        }
    }

    private sealed record CounterChanged(int Delta) : IDomainEvent
    {
        public Guid EventId { get; } = Guid.NewGuid();

        public DateTimeOffset OccurredOn { get; } = DateTimeOffset.UtcNow;
    }
}

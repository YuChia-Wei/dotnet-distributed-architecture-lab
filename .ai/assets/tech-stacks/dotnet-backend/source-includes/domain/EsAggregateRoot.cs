using System;
using System.Collections.Generic;

namespace BuildingBlocks.Domain;

/// <summary>
/// Optional mechanical support for an event-sourced Aggregate.
/// Product invariants and event transition logic remain target-owned.
/// </summary>
public abstract class EsAggregateRoot<TId> : IAggregateRoot<TId>
    where TId : notnull
{
    private readonly List<IDomainEvent> _pendingEvents = [];

    public abstract TId Id { get; }

    /// <summary>
    /// Gets the last committed event-stream version.
    /// Pending events are not included until a repository confirms the commit.
    /// </summary>
    public int Version { get; private set; }

    public IReadOnlyList<IDomainEvent> DomainEvents => _pendingEvents;

    protected IDomainEvent? LastDomainEvent =>
        _pendingEvents.Count == 0 ? null : _pendingEvents[^1];

    /// <summary>
    /// Rebuilds state from committed history without creating pending events.
    /// Call this from the derived reconstruction constructor body, after derived
    /// field initializers have executed.
    /// </summary>
    protected void Replay(IEnumerable<IDomainEvent> history)
    {
        ArgumentNullException.ThrowIfNull(history);

        if (Version != 0 || _pendingEvents.Count != 0)
        {
            throw new InvalidOperationException(
                "Replay can only initialize an aggregate with no committed or pending events.");
        }

        foreach (var @event in history)
        {
            ArgumentNullException.ThrowIfNull(@event);
            When(@event);
            Version++;
        }
    }

    /// <summary>
    /// Applies one new event to state and records it as pending.
    /// </summary>
    protected void Apply(IDomainEvent @event)
    {
        ArgumentNullException.ThrowIfNull(@event);
        When(@event);
        _pendingEvents.Add(@event);
    }

    /// <summary>
    /// Advances the committed version and clears pending events after durable
    /// persistence has succeeded.
    /// </summary>
    public void MarkChangesAsCommitted(int committedVersion)
    {
        var expectedVersion = checked(Version + _pendingEvents.Count);
        if (committedVersion != expectedVersion)
        {
            throw new InvalidOperationException(
                $"Committed version {committedVersion} does not match expected version {expectedVersion}.");
        }

        Version = committedVersion;
        _pendingEvents.Clear();
    }

    /// <summary>
    /// Performs a deterministic state transition. Business decisions and
    /// external I/O do not belong in this method.
    /// </summary>
    protected abstract void When(IDomainEvent @event);
}

using System;

namespace BuildingBlocks.Domain;

/// <summary>
/// Marks an immutable fact that occurred in the Domain.
/// </summary>
public interface IDomainEvent
{
    Guid EventId { get; }

    DateTimeOffset OccurredOn { get; }
}

namespace BuildingBlocks.Domain;

/// <summary>
/// Marks the public consistency boundary for an Aggregate.
/// </summary>
public interface IAggregateRoot<out TId> : IDomainEntity<TId>
    where TId : notnull
{
}

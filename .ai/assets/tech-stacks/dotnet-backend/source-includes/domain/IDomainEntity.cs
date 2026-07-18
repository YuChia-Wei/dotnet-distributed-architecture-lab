namespace BuildingBlocks.Domain;

/// <summary>
/// Exposes identity without imposing an entity base class.
/// </summary>
public interface IDomainEntity<out TId>
    where TId : notnull
{
    TId Id { get; }
}

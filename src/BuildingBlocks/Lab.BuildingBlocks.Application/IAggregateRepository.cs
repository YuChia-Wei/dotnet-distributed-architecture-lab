using Lab.BuildingBlocks.Domains;

namespace Lab.BuildingBlocks.Application;

/// <summary>Canonical write-side port for loading and persisting one aggregate root.</summary>
public interface IAggregateRepository<TAggregate, in TId>
    where TAggregate : IAggregateRoot<TId>
    where TId : notnull
{
    Task<TAggregate?> FindByIdAsync(
        TId id,
        CancellationToken cancellationToken = default);

    Task SaveAsync(
        TAggregate aggregate,
        CancellationToken cancellationToken = default);
}

/// <summary>Compatibility alias for existing aggregate repositories.</summary>
public interface IDomainRepository<TAggregate, in TId>
    : IAggregateRepository<TAggregate, TId>
    where TAggregate : IAggregateRoot<TId>
    where TId : notnull
{
}

namespace Lab.BuildingBlocks.Domains;

public abstract class AggregateRoot<TId>
    : DomainEntity<TId>, IAggregateRoot<TId> where TId : notnull
{
    protected AggregateRoot(TId id) : base(id)
    {
    }

    protected AggregateRoot()
    {
    }

    public int Version { get; protected set; }
}
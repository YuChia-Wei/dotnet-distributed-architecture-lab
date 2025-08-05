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

    public int Version { get; private set; }

    public void IncrementVersion()
    {
        this.Version++;
    }
}
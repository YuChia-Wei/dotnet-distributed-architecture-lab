using System.ComponentModel.DataAnnotations.Schema;

namespace Lab.BuildingBlocks.Domains;

public abstract class DomainEntity<TId>
    : IDomainEntity<TId> where TId : notnull
{
    private readonly List<IDomainEvent> _domainEvents = new();

    protected DomainEntity(TId id)
    {
        this.Id = id;
    }

    protected DomainEntity()
    {
    }

    [Column(Order = 0)]
    public TId Id { get; protected set; }

    public IReadOnlyCollection<IDomainEvent> DomainEvents => this._domainEvents.AsReadOnly();

    public void AddDomainEvent(IDomainEvent domainEvent)
    {
        this._domainEvents.Add(domainEvent);
    }

    public void RemoveDomainEvent(IDomainEvent domainEvent)
    {
        this._domainEvents.Remove(domainEvent);
    }

    public void ClearDomainEvents()
    {
        this._domainEvents.Clear();
    }
}
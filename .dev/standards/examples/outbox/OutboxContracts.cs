using System.Collections.Generic;

namespace Example.Shared.Outbox;

// TODO: Replace these placeholders with ezDDD .NET ports.
public interface IOutboxData<TId>
{
    TId Id { get; set; }
    List<DomainEventData> DomainEventDatas { get; set; }
    string StreamName { get; set; }
    long Version { get; set; }
}

public sealed class DomainEventData
{
}

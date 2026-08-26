using System.Collections.Generic;

namespace Example.Shared.Outbox;

// Framework-neutral placeholders; replace them with target-owned contracts.
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

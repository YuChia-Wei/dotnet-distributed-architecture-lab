using Example.Plans.Domain;
using Example.Tags.Domain;

namespace Example.Plans.Outbox;

public static class BootstrapConfig
{
    public static DomainEventTypeMapper Initialize()
    {
        var mapper = DomainEventTypeMapper.Create();

        foreach (var pair in PlanEvents.TypeMapper.Map)
        {
            mapper.Put(pair.Key, pair.Value);
        }

        foreach (var pair in TagEvents.TypeMapper.Map)
        {
            mapper.Put(pair.Key, pair.Value);
        }

        MessageDataMapper.SetMapper(mapper);
        DomainEventMapper.SetMapper(mapper);

        return mapper;
    }
}

// TODO: Replace these placeholders with ezDDD .NET ports.
public sealed class DomainEventTypeMapper
{
    private readonly Dictionary<string, Type> _map = new();

    public static DomainEventTypeMapper Create() => new();

    public void Put(string key, Type value) => _map[key] = value;
    public IReadOnlyDictionary<string, Type> Map => _map;
}

public static class MessageDataMapper
{
    public static void SetMapper(DomainEventTypeMapper mapper) { }
}

public static class DomainEventMapper
{
    public static void SetMapper(DomainEventTypeMapper mapper) { }
    public static Example.Shared.Outbox.DomainEventData ToData(object domainEvent) => new();
    public static object ToDomain(Example.Shared.Outbox.DomainEventData data) => new();
}

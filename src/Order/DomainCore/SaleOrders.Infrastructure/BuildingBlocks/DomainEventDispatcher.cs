using Lab.BuildingBlocks.Domains;
using Wolverine;

namespace SaleOrders.Infrastructure.BuildingBlocks;

/// <inheritdoc />
/// <remarks>
/// 由於涉及 IO，因此由 infra 端實作
/// </remarks>
public class DomainEventDispatcher(IMessageBus messageBus) : IDomainEventDispatcher
{
    /// <summary>
    /// 發布領域事件
    /// </summary>
    /// <param name="events"></param>
    /// <param name="ct"></param>
    /// <returns></returns>
    public async Task DispatchAsync(IEnumerable<IDomainEvent> events, CancellationToken ct = default)
    {
        foreach (var @event in events)
        {
            await messageBus.PublishAsync(@event);
        }
    }
}
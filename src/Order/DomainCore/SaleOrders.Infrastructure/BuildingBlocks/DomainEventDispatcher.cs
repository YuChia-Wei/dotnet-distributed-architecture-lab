using Lab.BuildingBlocks.Domains;

namespace SaleOrders.Infrastructure.BuildingBlocks;

/// <inheritdoc />
/// <remarks>
/// 由於涉及 IO，因此由 infra 端實作
/// </remarks>
public class DomainEventDispatcher : IDomainEventDispatcher
{
    /// <summary>
    /// 發布領域事件
    /// </summary>
    /// <param name="events"></param>
    /// <param name="ct"></param>
    /// <returns></returns>
    public Task DispatchAsync(IEnumerable<IDomainEvent> events, CancellationToken ct = default)
    {
        throw new NotImplementedException();
    }
}
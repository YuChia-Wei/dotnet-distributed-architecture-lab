using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using InventoryControl.Domains.DomainEvents;

namespace InventoryControl.Applications.DomainEventHandlers;

public class OrderPlacedEventHandler
{
    public static async Task HandleAsync(StockDecreased domainEvent, ILogger logger, CancellationToken cancellationToken)
    {
        logger.LogInformation("收到扣庫領域事件 {InventoryId}：{ProductId}, decreased {Qty}, CurrentStock = {CurrentStock}",
                               domainEvent.InventoryItemId, domainEvent.InventoryItemId, domainEvent.DecreasedQuantity, domainEvent.CurrentStock);
    }
}
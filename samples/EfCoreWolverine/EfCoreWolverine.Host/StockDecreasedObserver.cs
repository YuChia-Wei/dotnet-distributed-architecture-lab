using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Microsoft.Extensions.Logging;

namespace EfCoreWolverine.Host;

/// <summary>Demo-only observation of the event that came back through Kafka; no business side effects.</summary>
public static class StockDecreasedObserver
{
    public static void Handle(ProductStockDecreasedIntegrationEvent message,
        ILogger<ProductStockDecreasedIntegrationEvent> logger)
        => logger.LogInformation("Kafka delivered StockDecreased: inventory={InventoryId}, stock={Stock}",
            message.InventoryItemId, message.CurrentStock);
}

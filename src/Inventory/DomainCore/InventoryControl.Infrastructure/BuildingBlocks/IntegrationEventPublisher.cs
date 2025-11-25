using System.Threading.Tasks;
using Lab.BuildingBlocks.Integrations;
using Microsoft.Extensions.Logging;
using Wolverine;

namespace InventoryControl.Infrastructure.BuildingBlocks;

/// <inheritdoc />
public class IntegrationEventPublisher(IMessageBus messageBus, ILogger<IntegrationEventPublisher> logger) : IIntegrationEventPublisher
{
    /// <summary>
    /// 發布整合事件
    /// </summary>
    /// <typeparam name="T">欲發布的訊息型別，必須為參考型別</typeparam>
    /// <param name="integrationEvent">欲發布的訊息內容</param>
    /// <returns>代表非同步操作的工作物件</returns>
    public async Task PublishAsync(IIntegrationEvent integrationEvent)
    {
        logger.LogInformation("publish integration event: {IntegrationEvent}", integrationEvent);
        await messageBus.PublishAsync(integrationEvent);
    }
}
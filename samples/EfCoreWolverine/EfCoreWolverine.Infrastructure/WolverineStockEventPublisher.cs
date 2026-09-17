using EfCoreWolverine.Application;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Wolverine;

namespace EfCoreWolverine.Infrastructure;

/// <summary>Stages outgoing work through the enrolled message context; endpoints must use the durable outbox.</summary>
public sealed class WolverineStockEventPublisher(IMessageContext messages) : IStockEventPublisher
{
    public async Task PublishAsync(ProductStockDecreasedIntegrationEvent message, CancellationToken cancellationToken)
    {
        cancellationToken.ThrowIfCancellationRequested();
        await messages.PublishAsync(message);
    }
}

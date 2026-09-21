using EfCoreWolverine.Application;
using Microsoft.Extensions.Logging;

namespace EfCoreWolverine.Host;

public static class DecreaseStockHandler
{
    /// <summary>Completes expected business rejections; persistence and staging exceptions escape for rollback and retry.</summary>
    public static async Task Handle(DecreaseStockRequested message, IDecreaseStockUseCase useCase,
        ILogger<DecreaseStockRequested> logger, CancellationToken cancellationToken)
    {
        var result = await useCase.ExecuteAsync(
            new DecreaseStockInput(message.InventoryItemId, message.Quantity), cancellationToken);

        if (!result.Succeeded)
            logger.LogWarning("Stock request rejected: {ErrorCode}", result.ErrorCode);
    }
}

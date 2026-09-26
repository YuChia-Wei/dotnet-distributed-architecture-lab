using InventoryControl.Applications.Outbox;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Lab.BuildingBlocks.Integrations;

namespace InventoryControl.Applications.Receipts;

public sealed record ApplyGoodsReceiptInput(Guid ReceiptId, Guid PurchaseOrderId, Guid ProductId, int Quantity);

public sealed record ApplyGoodsReceiptOutput(Guid ReceiptId, Guid InventoryItemId, int ResultingStock, bool WasAlreadyProcessed);

/// <summary>Commits a physical receipt, its durable identity, stock change, and outgoing event together.</summary>
public interface IInventoryGoodsReceiptStore
{
    Task<ApplyGoodsReceiptOutput> ApplyAndStageAsync(
        ApplyGoodsReceiptInput input,
        Func<ApplyGoodsReceiptOutput, InventoryOutboxMessage> successfulMessageFactory,
        CancellationToken cancellationToken);
}

public interface IApplyGoodsReceiptUseCase
{
    Task<ApplyGoodsReceiptOutput> ExecuteAsync(ApplyGoodsReceiptInput input, CancellationToken cancellationToken);
}

public sealed class ApplyGoodsReceiptUseCase(IInventoryGoodsReceiptStore store) : IApplyGoodsReceiptUseCase
{
    public Task<ApplyGoodsReceiptOutput> ExecuteAsync(ApplyGoodsReceiptInput input, CancellationToken cancellationToken)
    {
        ArgumentNullException.ThrowIfNull(input);
        if (input.ReceiptId == Guid.Empty || input.PurchaseOrderId == Guid.Empty || input.ProductId == Guid.Empty)
        {
            throw new InventoryGoodsReceiptException("ReceiptIdentityRequired");
        }

        if (input.Quantity <= 0)
        {
            throw new InventoryGoodsReceiptException("ReceiptQuantityMustBePositive");
        }

        return store.ApplyAndStageAsync(
            input,
            outcome => new InventoryOutboxMessage(
                new ProductStockIncreasedIntegrationEvent(
                    outcome.InventoryItemId,
                    input.ProductId,
                    input.Quantity,
                    outcome.ResultingStock),
                new IntegrationMessageDelivery(input.ReceiptId, input.ProductId.ToString("N"))),
            cancellationToken);
    }
}

/// <summary>Diagnosable receipt failure; the consumer must not acknowledge it as an applied receipt.</summary>
public sealed class InventoryGoodsReceiptException(string code, Exception? innerException = null)
    : Exception(code, innerException)
{
    public string Code { get; } = code;
}

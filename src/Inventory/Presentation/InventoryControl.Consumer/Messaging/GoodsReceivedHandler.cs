using InventoryControl.Applications.Receipts;
using Lab.BoundedContextContracts.Procurement.IntegrationEvents;

namespace InventoryControl.Consumer.Messaging;

/// <summary>Maps Procurement's physical receipt fact to Inventory's own receipt operation.</summary>
public sealed class GoodsReceivedHandler
{
    public Task HandleAsync(
        GoodsReceived message,
        IApplyGoodsReceiptUseCase useCase,
        CancellationToken cancellationToken)
        => useCase.ExecuteAsync(
            new ApplyGoodsReceiptInput(
                message.ReceiptId,
                message.PurchaseOrderId,
                message.ProductId,
                message.Quantity),
            cancellationToken);
}

using InventoryControl.Applications.Receipts;
using Lab.BoundedContextContracts.Procurement.IntegrationEvents;

namespace InventoryControl.Consumer.Messaging;

/// <summary>將採購實際收貨事實轉為庫存端的收貨操作。</summary>
public sealed class GoodsReceivedHandler
{
    /// <summary>以來源收貨識別執行一次庫存端入庫操作。</summary>
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

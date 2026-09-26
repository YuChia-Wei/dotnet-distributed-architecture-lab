using InventoryControl.Applications.Outbox;
using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using Lab.BuildingBlocks.Integrations;

namespace InventoryControl.Applications.Receipts;

/// <summary>表示待入庫的實際收貨識別與數量。</summary>
public sealed record ApplyGoodsReceiptInput(Guid ReceiptId, Guid PurchaseOrderId, Guid ProductId, int Quantity);

/// <summary>表示已儲存的收貨入庫結果與重播狀態。</summary>
public sealed record ApplyGoodsReceiptOutput(Guid ReceiptId, Guid InventoryItemId, int ResultingStock, bool WasAlreadyProcessed);

/// <summary>在同一交易中提交收貨識別、庫存變動與對外事件。</summary>
public interface IInventoryGoodsReceiptStore
{
    /// <summary>套用收貨並保存對外事件；相同收貨重播只回傳原結果。</summary>
    Task<ApplyGoodsReceiptOutput> ApplyAndStageAsync(
        ApplyGoodsReceiptInput input,
        Func<ApplyGoodsReceiptOutput, InventoryOutboxMessage> successfulMessageFactory,
        CancellationToken cancellationToken);
}

/// <summary>定義實際收貨入庫的應用程式入口。</summary>
public interface IApplyGoodsReceiptUseCase
{
    /// <summary>驗證並套用實際收貨。</summary>
    Task<ApplyGoodsReceiptOutput> ExecuteAsync(ApplyGoodsReceiptInput input, CancellationToken cancellationToken);
}

/// <summary>驗證收貨內容並建立庫存增加事件的預設實作。</summary>
public sealed class ApplyGoodsReceiptUseCase(IInventoryGoodsReceiptStore store) : IApplyGoodsReceiptUseCase
{
    /// <summary>以固定收貨識別提交入庫要求。</summary>
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

/// <summary>可辨識的收貨入庫失敗；消費端不得將其視為成功。</summary>
public sealed class InventoryGoodsReceiptException(string code, Exception? innerException = null)
    : Exception(code, innerException)
{
    /// <summary>取得穩定的失敗代碼。</summary>
    public string Code { get; } = code;
}

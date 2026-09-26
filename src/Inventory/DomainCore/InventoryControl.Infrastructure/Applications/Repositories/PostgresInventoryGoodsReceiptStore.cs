using System.Data;
using InventoryControl.Applications.Outbox;
using InventoryControl.Applications.Receipts;
using InventoryControl.Infrastructure.Persistence;
using Lab.BuildingBlocks.Application;
using Microsoft.EntityFrameworkCore;
using Npgsql;

namespace InventoryControl.Infrastructure.Applications.Repositories;

/// <summary>Owns the receipt identity and all of its Inventory effects in one database transaction.</summary>
public sealed class PostgresInventoryGoodsReceiptStore(
    InventoryDbContext context,
    IDomainEventDispatcher dispatcher) : IInventoryGoodsReceiptStore
{
    public async Task<ApplyGoodsReceiptOutput> ApplyAndStageAsync(
        ApplyGoodsReceiptInput input,
        Func<ApplyGoodsReceiptOutput, InventoryOutboxMessage> successfulMessageFactory,
        CancellationToken cancellationToken)
    {
        try
        {
            await using var transaction = await context.Database.BeginTransactionAsync(IsolationLevel.ReadCommitted, cancellationToken);
            var claimed = await context.Database.ExecuteSqlAsync($"""
                INSERT INTO inventorygoodsreceipts (receiptid, purchaseorderid, productid, quantity)
                VALUES ({input.ReceiptId}, {input.PurchaseOrderId}, {input.ProductId}, {input.Quantity})
                ON CONFLICT (receiptid) DO NOTHING;
                """, cancellationToken);

            if (claimed == 0)
            {
                var replay = await ReadExistingAsync(input, cancellationToken);
                await transaction.CommitAsync(cancellationToken);
                return replay;
            }

            var rows = await context.InventoryItems.FromSql($"""
                SELECT id, productid, stock FROM inventoryitems WHERE productid = {input.ProductId} FOR UPDATE
                """).AsNoTracking().ToListAsync(cancellationToken);
            var item = rows.SingleOrDefault()
                ?? throw new InventoryGoodsReceiptException("InventoryItemNotFound");

            if (item.Stock > int.MaxValue - input.Quantity)
            {
                throw new InventoryGoodsReceiptException("StockOverflow");
            }

            var expectedStock = item.Stock;
            item.IncreaseStock(input.Quantity);
            context.DetachInventoryItem(item.Id);
            var affected = await context.InventoryItems
                .Where(row => row.Id == item.Id && row.Stock == expectedStock)
                .ExecuteUpdateAsync(setters => setters.SetProperty(row => row.Stock, item.Stock), cancellationToken);
            if (affected != 1)
            {
                throw new InventoryStockConcurrencyException(item.Id, expectedStock);
            }

            var outcome = new ApplyGoodsReceiptOutput(input.ReceiptId, item.Id, item.Stock, false);
            await context.GoodsReceipts.Where(row => row.ReceiptId == input.ReceiptId)
                .ExecuteUpdateAsync(setters => setters
                    .SetProperty(row => row.InventoryItemId, item.Id)
                    .SetProperty(row => row.ResultingStock, item.Stock)
                    .SetProperty(row => row.CompletedAt, DateTime.UtcNow), cancellationToken);
            var message = successfulMessageFactory(outcome)
                ?? throw new InvalidOperationException("A completed receipt requires an outbox message.");
            var staged = await InventoryOutboxWriter.StageAsync(context, message, cancellationToken);
            if (staged != 1)
            {
                throw new InventoryGoodsReceiptException("OutboxIdentityConflict");
            }
            await transaction.CommitAsync(cancellationToken);
            context.ChangeTracker.Clear();

            await dispatcher.DispatchAsync(item.DomainEvents.ToArray(), cancellationToken);
            item.ClearDomainEvents();
            return outcome;
        }
        catch (Exception exception) when (exception is NpgsqlException || exception is DbUpdateException { InnerException: NpgsqlException })
        {
            context.ChangeTracker.Clear();
            throw new InventoryGoodsReceiptException("ReceiptStorageUnavailable", exception);
        }
        catch
        {
            context.ChangeTracker.Clear();
            throw;
        }
    }

    private async Task<ApplyGoodsReceiptOutput> ReadExistingAsync(
        ApplyGoodsReceiptInput input,
        CancellationToken cancellationToken)
    {
        var row = await context.GoodsReceipts.AsNoTracking()
            .SingleAsync(receipt => receipt.ReceiptId == input.ReceiptId, cancellationToken);
        if (row.PurchaseOrderId != input.PurchaseOrderId || row.ProductId != input.ProductId || row.Quantity != input.Quantity)
        {
            throw new InventoryGoodsReceiptException("ReceiptIdentityConflict");
        }

        if (row.CompletedAt is null || row.InventoryItemId is null || row.ResultingStock is null)
        {
            throw new InventoryGoodsReceiptException("ReceiptIncomplete");
        }

        return new ApplyGoodsReceiptOutput(row.ReceiptId, row.InventoryItemId.Value, row.ResultingStock.Value, true);
    }
}

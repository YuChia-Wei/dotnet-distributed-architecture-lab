using System;
using InventoryControl.Domains.DomainEvents;
using InventoryControl.Domains.DomainResults;
using Lab.BuildingBlocks.Domains;

namespace InventoryControl.Domains;

/// <summary>
/// 貨品庫存 Aggregate Root
/// </summary>
public class InventoryItem : AggregateRoot<Guid>
{
    /// <summary>
    /// ctor (for ORM)
    /// </summary>
    private InventoryItem() { }

    public InventoryItem(Guid productId, int stock)
    {
        this.Id = Guid.CreateVersion7();
        this.ProductId = productId;
        this.Stock = stock;
    }

    public Guid ProductId { get; private set; }

    public int Stock { get; private set; }

    /// <summary>
    /// Reduces the product's stock by the specified quantity.
    /// </summary>
    /// <param name="quantity">The amount by which to decrease the stock.</param>
    /// <exception cref="InvalidOperationException">Thrown when the specified quantity is greater than the current stock.</exception>
    public StockDecreaseResult DecreaseStock(int quantity)
    {
        if (quantity < 0)
        {
            throw new InvalidOperationException("Invalid quantity.");
        }

        if (this.Stock < quantity)
        {
            // 預期中的業務結果：庫存不足，不建議用 Exception
            return StockDecreaseResult.Fail(
                "InsufficientStock",
                "Available stock is not enough.");
        }

        this.Stock -= quantity;

        this.AddDomainEvent(new StockDecreased(this.Id, this.ProductId, quantity, this.Stock));

        return StockDecreaseResult.Success();
    }

    /// <summary>
    /// Increases the product's stock by the specified quantity.
    /// </summary>
    /// <param name="quantity">The amount by which to increase the stock.</param>
    public StockIncreaseResult IncreaseStock(int quantity)
    {
        this.Stock += quantity;

        this.AddDomainEvent(new StockIncreased(this.Id, this.ProductId, quantity, this.Stock));

        return StockIncreaseResult.Success();
    }

    /// <summary>
    /// 將商品庫存補回指定數量。
    /// </summary>
    /// <param name="quantity">補回的庫存數量。</param>
    public StockReturnResult Restock(int quantity)
    {
        this.Stock += quantity;

        this.AddDomainEvent(new StockReturned(this.Id, this.ProductId, quantity, this.Stock));

        return StockReturnResult.Success();
    }
}
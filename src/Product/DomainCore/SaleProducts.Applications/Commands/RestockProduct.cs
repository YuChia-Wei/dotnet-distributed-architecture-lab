using Microsoft.Extensions.Logging;
using SaleProducts.Applications.Repositories;

namespace SaleProducts.Applications.Commands;

/// <summary>
/// 補回商品庫存的命令。
/// </summary>
/// <param name="ProductId">商品識別碼。</param>
/// <param name="Quantity">補回的庫存數量。</param>
public record RestockProductCommand(Guid ProductId, int Quantity);

/// <summary>
/// 補貨命令的處理常式。
/// </summary>
public class RestockProductCommandHandler
{
    private readonly ILogger<RestockProductCommandHandler> _logger;
    private readonly IProductDomainRepository _repository;

    /// <summary>
    /// 建立 <see cref="RestockProductCommandHandler" />。
    /// </summary>
    /// <param name="repository">商品領域儲存庫。</param>
    /// <param name="logger">紀錄器。</param>
    public RestockProductCommandHandler(IProductDomainRepository repository, ILogger<RestockProductCommandHandler> logger)
    {
        this._repository = repository;
        this._logger = logger;
    }

    /// <summary>
    /// 處理補貨命令並更新商品庫存。
    /// </summary>
    /// <param name="command">補貨命令。</param>
    public async Task Handle(RestockProductCommand command)
    {
        if (command.Quantity <= 0)
        {
            this._logger.LogWarning("忽略補貨命令，商品 {ProductId} 指定的補貨數量 {Quantity} 無效。", command.ProductId, command.Quantity);
            return;
        }

        var product = await this._repository.GetByIdAsync(command.ProductId);
        if (product is null)
        {
            this._logger.LogWarning("找不到商品 {ProductId}，無法補回庫存。", command.ProductId);
            return;
        }

        product.Restock(command.Quantity);
        await this._repository.UpdateAsync(product);

        this._logger.LogInformation("已補回商品 {ProductId} 的庫存，增加數量 {Quantity}。", command.ProductId, command.Quantity);
    }
}
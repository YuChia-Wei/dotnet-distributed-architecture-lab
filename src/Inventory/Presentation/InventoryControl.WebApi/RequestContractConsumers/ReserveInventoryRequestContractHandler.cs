using System.Threading.Tasks;
using InventoryControl.Applications.UseCases;
using Lab.BoundedContextContracts.Inventory.Interactions;

namespace InventoryControl.WebApi.RequestContractConsumers;

/// <summary>
/// 處理保留庫存 request contract 的 consumer。
/// </summary>
public class ReserveInventoryRequestContractHandler(IDecreaseStockUseCase useCase)
{
    /// <summary>
    /// 處理保留庫存請求並回傳結果。
    /// </summary>
    /// <param name="request">保留庫存請求契約。</param>
    /// <param name="cancellationToken">取消權杖。</param>
    /// <returns>保留庫存回應契約。</returns>
    public async Task<ReserveInventoryResponseContract> HandleAsync(ReserveInventoryRequestContract request, CancellationToken cancellationToken)
    {
        var resultDto = await useCase.ExecuteAsync(new DecreaseStockInput(request.ProductId, request.Quantity), cancellationToken);
        return new ReserveInventoryResponseContract
        {
            Result = resultDto.IsSuccess
        };
    }
}

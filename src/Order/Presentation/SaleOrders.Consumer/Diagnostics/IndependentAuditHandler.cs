using Lab.BuildingBlocks.Integrations.Diagnostics;
using SaleOrders.Applications.Diagnostics;

namespace SaleOrders.Consumer.Diagnostics;

/// <summary>在獨立的 Wolverine 佇列與重試流程處理原始外部事件。</summary>
public static class IndependentAuditHandler
{
    /// <summary>將外部事件映射為使用案例輸入並等待處理完成。</summary>
    public static Task Handle(IndependentWorkRequested message, IWriteParallelAuditUseCase useCase,
        CancellationToken cancellationToken)
        => useCase.ExecuteAsync(new ParallelWorkInput(message.ProbeId), cancellationToken);
}

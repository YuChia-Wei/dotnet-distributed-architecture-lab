using Lab.BuildingBlocks.Integrations.Diagnostics;
using SaleOrders.Applications.Diagnostics;

namespace SaleOrders.Consumer.Diagnostics;

/// <summary>接收相同的原始外部事件，獨立於稽核作業處理統計。</summary>
public static class IndependentStatisticsHandler
{
    /// <summary>將外部事件映射為使用案例輸入並等待處理完成。</summary>
    public static Task Handle(IndependentWorkRequested message, IRecordParallelStatisticsUseCase useCase,
        CancellationToken cancellationToken)
        => useCase.ExecuteAsync(new ParallelWorkInput(message.ProbeId), cancellationToken);
}

using Lab.BuildingBlocks.Integrations.Diagnostics;
using Microsoft.Extensions.DependencyInjection;
using SaleOrders.Applications.Diagnostics;

namespace SaleOrders.Consumer.Diagnostics;

/// <summary>示範單次事件接收等待兩項獨立使用案例，各自使用獨立服務範圍。</summary>
/// <remarks>失敗時會重試整個事件，因此成功分支的副作用必須可安全重複。</remarks>
public static class WhenAllWorkHandler
{
    /// <summary>將外部事件映射為使用案例輸入並等待處理完成。</summary>
    public static Task Handle(WhenAllWorkRequested message, IServiceScopeFactory scopes,
        CancellationToken cancellationToken)
        => Task.WhenAll(WriteAuditAsync(message.ProbeId, scopes, cancellationToken),
            RecordStatisticsAsync(message.ProbeId, scopes, cancellationToken));

    private static async Task WriteAuditAsync(Guid probeId, IServiceScopeFactory scopes,
        CancellationToken cancellationToken)
    {
        await using var scope = scopes.CreateAsyncScope();
        var useCase = scope.ServiceProvider.GetRequiredService<IWriteParallelAuditUseCase>();
        await useCase.ExecuteAsync(new ParallelWorkInput(probeId), cancellationToken);
    }

    private static async Task RecordStatisticsAsync(Guid probeId, IServiceScopeFactory scopes,
        CancellationToken cancellationToken)
    {
        await using var scope = scopes.CreateAsyncScope();
        var useCase = scope.ServiceProvider.GetRequiredService<IRecordParallelStatisticsUseCase>();
        await useCase.ExecuteAsync(new ParallelWorkInput(probeId), cancellationToken);
    }
}

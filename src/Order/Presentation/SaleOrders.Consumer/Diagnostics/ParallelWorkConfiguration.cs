using Microsoft.Extensions.DependencyInjection;
using SaleOrders.Applications.Diagnostics;
using Wolverine;

namespace SaleOrders.Consumer.Diagnostics;

/// <summary>註冊兩種範例執行模型，沿用既有外部事件訂閱。</summary>
public static class ParallelWorkConfiguration
{
    /// <summary>稽核工作專用的處理佇列。</summary>
    public const string AuditQueue = "parallel-work-audit";
    /// <summary>統計工作專用的處理佇列。</summary>
    public const string StatisticsQueue = "parallel-work-statistics";

    /// <summary>註冊兩項獨立使用案例及各自的範例介接器。</summary>
    public static void AddParallelWorkExamples(this IServiceCollection services)
    {
        services.AddSingleton<ParallelWorkStore>();
        services.AddScoped<ParallelWorkScope>();
        services.AddScoped<IParallelAuditWriter, DemoParallelAuditWriter>();
        services.AddScoped<IParallelStatisticsWriter, DemoParallelStatisticsWriter>();
        services.AddScoped<IWriteParallelAuditUseCase, WriteParallelAuditUseCase>();
        services.AddScoped<IRecordParallelStatisticsUseCase, RecordParallelStatisticsUseCase>();
    }

    /// <summary>分離原始事件的處理器，由 Wolverine 執行外部入站事件分派。</summary>
    public static void ConfigureParallelWorkExamples(this WolverineOptions options)
    {
        options.MultipleHandlerBehavior = MultipleHandlerBehavior.Separated;
        options.LocalQueue(AuditQueue).AddStickyHandler(typeof(IndependentAuditHandler));
        options.LocalQueue(StatisticsQueue).AddStickyHandler(typeof(IndependentStatisticsHandler));
    }
}

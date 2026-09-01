using Wolverine;
using Wolverine.ErrorHandling;

namespace SaleOrders.Consumer.Messaging;

/// <summary>定義 Orders Consumer 的 Wolverine 訊息處理失敗政策。</summary>
public static class ConsumerFailurePolicy
{
    private static readonly TimeSpan[] TransientRetrySchedule =
    [
        TimeSpan.FromMilliseconds(100),
        TimeSpan.FromMilliseconds(500),
        TimeSpan.FromSeconds(2)
    ];

    /// <summary>取得暫時性逾時錯誤的依序重試間隔。</summary>
    public static IReadOnlyList<TimeSpan> TransientRetryDelays { get; } =
        Array.AsReadOnly(TransientRetrySchedule);

    /// <summary>未分類例外在移入錯誤佇列前的立即重試次數。</summary>
    public const int UnhandledExceptionRetryCount = 1;

    /// <summary>將 Consumer 的有限重試與錯誤佇列政策加入 Wolverine。</summary>
    /// <param name="options">要設定的 Wolverine 選項。</param>
    public static void Configure(WolverineOptions options)
    {
        ArgumentNullException.ThrowIfNull(options);

        // Wolverine evaluates matching rules in registration order, so the
        // transient policy must be registered before the general fallback.
        options.OnException<TimeoutException>()
            .RetryWithCooldown(TransientRetrySchedule)
            .Then.MoveToErrorQueue();

        options.OnException<Exception>()
            .RetryTimes(UnhandledExceptionRetryCount)
            .Then.MoveToErrorQueue();
    }
}

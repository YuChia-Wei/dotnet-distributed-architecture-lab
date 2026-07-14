using InventoryControl.Applications.Reservations;
using Wolverine;
using Wolverine.ErrorHandling;

namespace InventoryControl.Infrastructure.Messaging;

public static class InventoryReservationFailurePolicy
{
    public static readonly TimeSpan[] RetryDelays =
    [
        TimeSpan.FromMilliseconds(100),
        TimeSpan.FromMilliseconds(500),
        TimeSpan.FromSeconds(2)
    ];

    public static void Configure(WolverineOptions options)
    {
        options.OnException<InventoryReservationTransientException>()
            .RetryWithCooldown(RetryDelays)
            .Then.MoveToErrorQueue();
    }
}

using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
using InventoryControl.Applications.Outbox;
using Lab.BuildingBlocks.Integrations;

namespace InventoryControl.Applications.Reservations;

public sealed record ReserveInventoryInput(Guid OperationId, Guid ProductId, int Quantity);

public sealed record ReserveInventoryOutput(
    Guid OperationId,
    bool IsSuccess,
    int? RemainingStock,
    string? FailureReason,
    bool WasAlreadyProcessed);

public sealed record InventoryReservationOutcome(
    Guid OperationId,
    Guid ProductId,
    int Quantity,
    Guid? InventoryItemId,
    bool IsSuccess,
    int? RemainingStock,
    string? FailureReason,
    bool WasAlreadyProcessed);

/// <summary>
/// Resolves a reservation and atomically stages its successful integration event.
/// </summary>
/// <remarks>
/// The port describes the outbox capability. Database transaction or Unit of Work mechanics remain
/// private to the Infrastructure adapter.
/// </remarks>
public interface IInventoryReservationOutbox
{
    Task<InventoryReservationOutcome> ReserveAndStageAsync(
        Guid operationId,
        Guid productId,
        int quantity,
        Func<InventoryReservationOutcome, InventoryOutboxMessage> successfulMessageFactory,
        CancellationToken cancellationToken);
}

public interface IReserveInventoryUseCase
{
    Task<ReserveInventoryOutput> ExecuteAsync(
        ReserveInventoryInput input,
        CancellationToken cancellationToken);
}

public sealed class ReserveInventoryUseCase(
    IInventoryReservationOutbox outbox) : IReserveInventoryUseCase
{
    public async Task<ReserveInventoryOutput> ExecuteAsync(
        ReserveInventoryInput input,
        CancellationToken cancellationToken)
    {
        if (input.OperationId == Guid.Empty)
        {
            return Invalid(input.OperationId, "OperationIdRequired");
        }

        if (input.ProductId == Guid.Empty)
        {
            return Invalid(input.OperationId, "ProductIdRequired");
        }

        if (input.Quantity <= 0)
        {
            return Invalid(input.OperationId, "QuantityMustBePositive");
        }

        var outcome = await outbox.ReserveAndStageAsync(
            input.OperationId,
            input.ProductId,
            input.Quantity,
            successfulOutcome => new InventoryOutboxMessage(
                new ProductStockDecreasedIntegrationEvent(
                    successfulOutcome.InventoryItemId!.Value,
                    successfulOutcome.ProductId,
                    successfulOutcome.Quantity,
                    successfulOutcome.RemainingStock!.Value),
                new IntegrationMessageDelivery(
                    successfulOutcome.OperationId,
                    successfulOutcome.ProductId.ToString("N"))),
            cancellationToken);

        return new ReserveInventoryOutput(
            outcome.OperationId,
            outcome.IsSuccess,
            outcome.RemainingStock,
            outcome.FailureReason,
            outcome.WasAlreadyProcessed);
    }

    private static ReserveInventoryOutput Invalid(Guid operationId, string reason)
    {
        return new ReserveInventoryOutput(operationId, false, null, reason, false);
    }
}

public sealed class InventoryReservationTransientException : Exception
{
    public InventoryReservationTransientException(string message, Exception innerException)
        : base(message, innerException)
    {
    }
}

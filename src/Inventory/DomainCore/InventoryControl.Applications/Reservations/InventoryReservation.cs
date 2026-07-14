using Lab.BoundedContextContracts.Inventory.IntegrationEvents;
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

public interface IInventoryReservationRepository
{
    Task<InventoryReservationOutcome> ReserveAsync(
        Guid operationId,
        Guid productId,
        int quantity,
        CancellationToken cancellationToken);
}

public interface IReserveInventoryUseCase
{
    Task<ReserveInventoryOutput> ExecuteAsync(
        ReserveInventoryInput input,
        CancellationToken cancellationToken);
}

public sealed class ReserveInventoryUseCase(
    IInventoryReservationRepository repository,
    IIntegrationEventPublisher publisher) : IReserveInventoryUseCase
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

        var outcome = await repository.ReserveAsync(
            input.OperationId,
            input.ProductId,
            input.Quantity,
            cancellationToken);

        if (outcome.IsSuccess)
        {
            await publisher.PublishAsync(
                new ProductStockDecreasedIntegrationEvent(
                    outcome.InventoryItemId!.Value,
                    outcome.ProductId,
                    outcome.Quantity,
                    outcome.RemainingStock!.Value),
                new IntegrationMessageDelivery(outcome.OperationId, outcome.ProductId.ToString("N")));
        }

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

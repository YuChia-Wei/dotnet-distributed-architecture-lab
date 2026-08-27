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

public interface IInventoryReservationTransactionFactory
{
    Task<IInventoryReservationTransaction> BeginAsync(CancellationToken cancellationToken);
}

public interface IInventoryReservationTransaction : IAsyncDisposable
{
    Task<InventoryReservationOutcome> ReserveAsync(
        Guid operationId,
        Guid productId,
        int quantity,
        CancellationToken cancellationToken);

    Task StageAsync(
        IIntegrationEvent integrationEvent,
        IntegrationMessageDelivery delivery,
        CancellationToken cancellationToken);

    Task CommitAsync(CancellationToken cancellationToken);
}

public interface IReserveInventoryUseCase
{
    Task<ReserveInventoryOutput> ExecuteAsync(
        ReserveInventoryInput input,
        CancellationToken cancellationToken);
}

public sealed class ReserveInventoryUseCase(
    IInventoryReservationTransactionFactory transactionFactory) : IReserveInventoryUseCase
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

        await using var transaction = await transactionFactory.BeginAsync(cancellationToken);
        var outcome = await transaction.ReserveAsync(
            input.OperationId,
            input.ProductId,
            input.Quantity,
            cancellationToken);

        if (outcome.IsSuccess)
        {
            await transaction.StageAsync(
                new ProductStockDecreasedIntegrationEvent(
                    outcome.InventoryItemId!.Value,
                    outcome.ProductId,
                    outcome.Quantity,
                    outcome.RemainingStock!.Value),
                new IntegrationMessageDelivery(outcome.OperationId, outcome.ProductId.ToString("N")),
                cancellationToken);
        }

        await transaction.CommitAsync(cancellationToken);

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

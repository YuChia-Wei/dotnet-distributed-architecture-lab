namespace EfCoreWolverine.Application;

public interface IDecreaseStockUseCase
{
    Task<DecreaseStockOutput> ExecuteAsync(
        DecreaseStockInput input,
        CancellationToken cancellationToken);
}

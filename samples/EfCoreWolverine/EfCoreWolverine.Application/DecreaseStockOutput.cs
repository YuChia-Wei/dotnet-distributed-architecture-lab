namespace EfCoreWolverine.Application;

public sealed record DecreaseStockOutput(bool Succeeded, int? CurrentStock, string? ErrorCode);

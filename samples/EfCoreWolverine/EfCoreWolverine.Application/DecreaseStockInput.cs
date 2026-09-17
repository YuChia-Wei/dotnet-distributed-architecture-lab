namespace EfCoreWolverine.Application;

public sealed record DecreaseStockInput(Guid InventoryItemId, int Quantity);

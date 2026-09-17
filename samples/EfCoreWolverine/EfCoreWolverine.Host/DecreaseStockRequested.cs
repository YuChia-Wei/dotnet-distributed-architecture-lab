namespace EfCoreWolverine.Host;

/// <summary>A delivery contract, deliberately separate from the application input.</summary>
public sealed record DecreaseStockRequested(Guid InventoryItemId, int Quantity);

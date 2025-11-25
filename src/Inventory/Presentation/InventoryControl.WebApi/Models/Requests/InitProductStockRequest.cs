namespace InventoryControl.WebApi.Models.Requests;

public record InitProductStockRequest(int Stock);
public record ProductRestockRequest(int Stock);
public record IncreaseStockRequest(int Stock);
public record DecreaseStockRequest(int Stock);
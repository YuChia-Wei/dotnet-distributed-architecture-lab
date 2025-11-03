// In project: BC-Contracts/Lab.BoundedContextContracts.Products (New Project)
// Or maybe in an existing one like Lab.BoundedContextContracts.Orders.
// Based on AGENTS.md, there is no Lab.BoundedContextContracts.Products, I should probably create it.
// For now, I will just define the contracts. The creation of the project will be a task in tasks.md.

namespace Lab.BoundedContextContracts.Products.IntegrationEvents;

public record ProductItem(Guid ProductId, int Quantity);

public record ProductStockDeducted(
    Guid OrderId,
    List<ProductItem> Products);

public record ProductStockDeductionFailed(
    Guid OrderId,
    string Reason,
    List<ProductItem> Products);

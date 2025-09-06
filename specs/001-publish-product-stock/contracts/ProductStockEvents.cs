// In project: BC-Contracts/Lab.MessageSchemas.Products (New Project)
// Or maybe in an existing one like Lab.MessageSchemas.Orders.
// Based on AGENTS.md, there is no Lab.MessageSchemas.Products, I should probably create it.
// For now, I will just define the contracts. The creation of the project will be a task in tasks.md.

namespace Lab.MessageSchemas.Products.IntegrationEvents;

public record ProductItem(Guid ProductId, int Quantity);

public record ProductStockDeducted(
    Guid OrderId,
    List<ProductItem> Products);

public record ProductStockDeductionFailed(
    Guid OrderId,
    string Reason,
    List<ProductItem> Products);

# Data Models: Product Stock Events

This document defines the data structures for events related to product stock deduction.

## Event: `ProductStockDeducted`

-   **Description**: Published when stock has been successfully deducted for all products in an order.
-   **Namespace**: `Lab.MessageSchemas.Products.IntegrationEvents`
-   **Fields**:
    -   `OrderId` (Guid): The ID of the order for which stock was deducted.
    -   `Products` (List<ProductItem>): A list of the products and quantities deducted.

## Event: `ProductStockDeductionFailed`

-   **Description**: Published when stock deduction fails for any reason (e.g., insufficient stock, product not found).
-   **Namespace**: `Lab.MessageSchemas.Products.IntegrationEvents`
-   **Fields**:
    -   `OrderId` (Guid): The ID of the order for which stock deduction failed.
    -   `Reason` (string): A description of why the deduction failed.
    -   `Products` (List<ProductItem>): The original list of products from the order.

## Shared Object: `ProductItem`

-   **Description**: Represents a product and its quantity in an event.
-   **Fields**:
    -   `ProductId` (Guid): The ID of the product.
    -   `Quantity` (int): The quantity of the product.

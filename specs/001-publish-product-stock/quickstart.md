# Quickstart: Testing Product Stock Deduction

This guide explains how to test the product stock deduction feature.

## Prerequisites

-   The application is running (`docker-compose up`).
-   You have access to the RabbitMQ (or Kafka) management UI.

## Testing Steps

1.  **Place an Order**:
    -   Use the `SaleOrders.WebApi` to place a new order with one or more products.
    -   Note the `OrderId` from the response.

2.  **Verify `OrderPlaced` Event**:
    -   In RabbitMQ, check that the `OrderPlaced` event was published.

3.  **Verify `ProductStockDeducted` Event**:
    -   The `SaleProducts.Consumer` will consume the `OrderPlaced` event.
    -   Check in RabbitMQ that a `ProductStockDeducted` event is published by the Product service.
    -   Verify the event contains the correct `OrderId`.

4.  **Verify Order Status**:
    -   The `SaleOrders.Consumer` will consume the `ProductStockDeducted` event.
    -   Query the `SaleOrders.WebApi` for the order details using the `OrderId`.
    -   Verify that the order status has been updated to "Allocated" (or the implemented equivalent).

## Testing Failure Scenarios

1.  **Insufficient Stock**:
    -   Manually adjust the stock of a product to be lower than the quantity in a new order.
    -   Place an order for that product.
    -   Verify that a `ProductStockDeductionFailed` event is published with a reason indicating insufficient stock.
    -   Verify the order status is updated to "Failed" (or similar).

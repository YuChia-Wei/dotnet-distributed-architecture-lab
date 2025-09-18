# Quickstart: Validating Stock Restoration

This guide provides the manual steps to test and validate the end-to-end stock restoration feature after an order is cancelled.

## Prerequisites

1.  **All services are running**: Use `docker-compose` to start the full environment, including:
    *   `SaleProducts.WebApi`
    *   `SaleOrders.WebApi`
    *   `SaleProducts.Consumer`
    *   PostgreSQL Database
    *   Message Broker (RabbitMQ or Kafka)
2.  **API Client**: An API client like `curl`, Postman, or the built-in `.http` files in the repository is required to interact with the Web APIs.

## Validation Steps

### Step 1: Check Initial Product Stock

1.  First, identify a product to use for the test (e.g., by querying `GET /api/products`).
2.  Note its `productId` and current `stock` level.
    
    **Example Request:**
    ```http
    GET http://localhost:5001/api/products/{your-product-id}
    ```

### Step 2: Create a Sales Order

1.  Create a new sales order that includes the product from Step 1. This will trigger the stock deduction logic.

    **Example Request:**
    ```http
    POST http://localhost:5002/api/orders
    Content-Type: application/json

    {
      "customerId": "a8d8a6e2-0b3a-4b9e-8b0c-6b2a3a7d8e7f",
      "lineItems": [
        {
          "productId": "{your-product-id}",
          "quantity": 2
        }
      ]
    }
    ```
2.  Note the `orderId` returned in the response.

### Step 3: Cancel the Sales Order

1.  Cancel the order you just created. This action will publish the `OrderCancelled` integration event.

    **Example Request:**
    ```http
    DELETE http://localhost:5002/api/orders/{your-order-id}
    ```

### Step 4: Verify Stock Restoration

1.  Wait a few moments for the `SaleProducts.Consumer` to process the `OrderCancelled` event.
2.  Query the product's details again.

    **Example Request:**
    ```http
    GET http://localhost:5001/api/products/{your-product-id}
    ```

### Expected Result

The `stock` level of the product should now be restored to its original value from Step 1. If the stock was 50 and the cancelled order contained 2 items, the stock should be 50 again.

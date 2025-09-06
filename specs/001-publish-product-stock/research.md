# Research: Publish Product Stock Deducted Event

## Unresolved Questions from Spec

### 1. Insufficient Stock Handling
-   **Question**: What happens when stock is insufficient for a product?
-   **Decision**: A `ProductStockDeductionFailed` integration event will be published.
-   **Rationale**: This allows downstream consumers (like the Order service) to be notified of the failure and take compensating action, such as marking the order as failed. This follows a choreography-based saga pattern.
-   **Alternatives considered**:
    -   Synchronous call: This would couple the services and reduce resilience.
    -   No event on failure: This would leave the order in a pending state indefinitely.

### 2. Non-Existent Product Handling
-   **Question**: What happens if the `OrderPlaced` event contains a product that does not exist?
-   **Decision**: This is considered a data integrity issue. The Product service will log a critical error and publish a `ProductStockDeductionFailed` event.
-   **Rationale**: The system should not have accepted an order for a non-existent product. This indicates a problem upstream. Publishing a failure event ensures the order is not left in a pending state.
-   **Alternatives considered**:
    -   Ignoring the missing product: This would lead to an incomplete order fulfillment without notification.

## Technology Best Practices

### WolverineFx Messaging
-   **Finding**: Wolverine is used for messaging. Events should be simple C# records. Handlers are discovered by convention.
-   **Decision**: We will use Wolverine to publish the `ProductStockDeducted` and `ProductStockDeductionFailed` events.

### CQRS
-   **Finding**: The project uses CQRS. The consumer will handle an integration event and likely dispatch a command internally.
-   **Decision**: The `SaleProducts.Consumer` will handle the `OrderPlaced` event and trigger a `DeductStockCommand`. The handler for this command will perform the stock deduction and publish the resulting event.

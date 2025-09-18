# Tasks: Product Stock Restoration on Order Cancellation

**Input**: Design documents from `/specs/003-product-consumer-ordercancelled/`

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Phase 3.1: Setup & Contracts
- [ ] T001 [P] Create the DTO file `src/BC-Contracts/Lab.MessageSchemas.Orders/DataTransferObjects/OrderDetailsResponse.cs` based on the definition in `specs/003-product-consumer-ordercancelled/contracts/OrderDetailsResponse.cs`.
- [ ] T002 [P] In the `SaleOrders.Applications` project, create a new query record `public record GetOrderDetailsQuery(Guid OrderId);` in a new file `src/Order/DomainCore/SaleOrders.Applications/Queries/GetOrderDetails.cs`.
- [ ] T003 [P] In the `SaleProducts.Domains` project, add a new public method `public void Restock(int quantity)` to the `Product` entity in `src/Product/DomainCore/SaleProducts.Domains/Product.cs`.
- [ ] T004 [P] In the `SaleProducts.Applications` project, create a new command record `public record RestockProductCommand(Guid ProductId, int Quantity);` in a new file `src/Product/DomainCore/SaleProducts.Applications/Commands/RestockProduct.cs`.

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T005 [P] Create a new test class `GetOrderDetailsEndpointTests` in `tests/SaleOrders.Tests/GetOrderDetailsEndpointTests.cs`. It should test that a `GET` request to `/api/orders/{orderId}` returns the correct order details. This test will fail until the endpoint is implemented.
- [ ] T006 [P] Create a new integration test class `OrderCancellationStockRestorationTests` in `tests/SaleProducts.Tests/OrderCancellationStockRestorationTests.cs`. This test should follow the end-to-end scenario described in `quickstart.md`. This test will fail.
- [ ] T007 [P] In `tests/SaleProducts.Domains.Tests/ProductTests.cs`, add a new unit test to verify that the `Restock` method correctly increases the product's stock quantity.

## Phase 3.3: Core Implementation (Order Context)
- [ ] T008 Implement the `GetOrderDetailsQueryHandler` class in `src/Order/DomainCore/SaleOrders.Applications/Queries/GetOrderDetails.cs`. This handler should fetch the order and its line items from the database and return an `OrderDetailsResponse`.
- [ ] T009 In `src/Order/Presentation/SaleOrders.WebApi/Controllers/OrdersController.cs`, implement a new public `GET` endpoint `[HttpGet("{orderId}")]` that takes a `Guid orderId`, sends the `GetOrderDetailsQuery`, and returns the result.

## Phase 3.4: Core Implementation (Product Context)
- [ ] T010 Create the `IOrderApiClient` interface and its implementation `OrderApiClient` in a new file `src/Product/DomainCore/SaleProducts.Infrastructure/Clients/OrderApiClient.cs`. This client will have one method `Task<OrderDetailsResponse> GetOrderDetailsAsync(Guid orderId);` that calls the endpoint created in T009.
- [ ] T011 Implement the `RestockProductCommandHandler` class in `src/Product/DomainCore/SaleProducts.Applications/Commands/RestockProduct.cs`. This handler should load the `Product` aggregate, call the `Restock` method, and save the changes.
- [ ] T012 Implement the `OrderCancelledHandler` class in `src/Product/Presentation/SaleProducts.Consumer/IntegrationEventHandlers/OrderCancelledHandler.cs`. This class will handle the `OrderCancelled` event. It must use the `IOrderApiClient` to get order details and then dispatch a `RestockProductCommand` for each line item in the response. Implement idempotency checks to avoid processing the same event twice.

## Phase 3.5: Polish & Verification
- [ ] T013 [P] Register the `IOrderApiClient` and its implementation for dependency injection in the `SaleProducts.Infrastructure` project's service extension method.
- [ ] T014 [P] Add DI registration for the `GetOrderDetailsQueryHandler` in the `SaleOrders.Applications` project's service extension method.
- [ ] T015 [P] Review all new public classes and methods and add XML comments in Traditional Chinese, as required by the project's contribution guidelines.
- [ ] T016 Run `dotnet test` from the root directory and ensure all tests, including the new ones, pass.
- [ ] T017 Manually verify the entire workflow by following the steps outlined in `specs/003-product-consumer-ordercancelled/quickstart.md`.

## Dependencies
- `T001`-`T004` (Setup) must be done before other tasks.
- `T005`-`T007` (Tests) must be done before `T008`-`T012` (Implementation).
- `T009` depends on `T008`.
- `T012` depends on `T010` and `T011`.
- `T013`-`T017` (Polish) must be done after implementation is complete.

## Parallel Example
```
# The following setup and test tasks can be run in parallel:
Task: "T001 [P] Create the DTO file src/BC-Contracts/Lab.MessageSchemas.Orders/DataTransferObjects/OrderDetailsResponse.cs"
Task: "T002 [P] In the SaleOrders.Applications project, create a new query record..."
Task: "T005 [P] Create a new test class GetOrderDetailsEndpointTests..."
Task: "T006 [P] Create a new integration test class OrderCancellationStockRestorationTests..."
```

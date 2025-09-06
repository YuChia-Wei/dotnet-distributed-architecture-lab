# Tasks: Publish Product Stock Deducted Event

**Input**: Design documents from `C:\Github\YuChia\dotnet-mq-arch-lab\specs\001-publish-product-stock\`

## Phase 3.1: Setup & Contracts
- [ ] T001: **Create Project**: Create a new .NET class library `Lab.MessageSchemas.Products` in `src/BC-Contracts/`.
- [ ] T002: **Add to Solution**: Add the `Lab.MessageSchemas.Products.csproj` to the `MQArchLab.slnx` solution file under the `BC-Contracts` solution folder.
- [ ] T003: **Define Events**: Move the event definitions from `specs/001-publish-product-stock/contracts/ProductStockEvents.cs` to a new file `IntegrationEvents.cs` inside the `Lab.MessageSchemas.Products` project.
- [ ] T004: **Add Dependencies**:
    - Add a project reference from `SaleProducts.Consumer` to `Lab.MessageSchemas.Products`.
    - Add a project reference from `SaleOrders.Consumer` to `Lab.MessageSchemas.Products`.
    - Add a project reference from `SaleProducts.Applications` to `Lab.MessageSchemas.Products`.

## Phase 3.2: Tests First (TDD)
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T005 [P]: **Integration Test (Product Stock Deduction)**: In a new test file in the `SaleProducts` test project, write an integration test that publishes an `OrderPlaced` event and asserts that a `ProductStockDeducted` event is published by the consumer when stock is sufficient.
- [ ] T006 [P]: **Integration Test (Product Stock Failure)**: In the same test file as T005, add a test case for when stock is insufficient. It should assert that a `ProductStockDeductionFailed` event is published.
- [ ] T007 [P]: **Integration Test (Order Status Update - Success)**: In a new test file in the `SaleOrders` test project, write an integration test that publishes a `ProductStockDeducted` event and asserts that the corresponding `Order`'s status is updated to `Allocated`.
- [ ] T008 [P]: **Integration Test (Order Status Update - Failure)**: In the same test file as T007, add a test that publishes a `ProductStockDeductionFailed` event and asserts that the `Order`'s status is updated to `Failed`.

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [ ] T009: **Create Command**: In `SaleProducts.Applications`, create a new command `DeductStockCommand(Guid OrderId, List<ProductItem> Products)` in a new `Commands` folder.
- [ ] T010: **Create Command Handler**: In `SaleProducts.Applications`, create the handler `DeductStockCommandHandler`. This handler will:
    - Load the `Product` aggregates.
    - Check if stock is sufficient.
    - If sufficient, deduct the stock from the `Product` aggregates and save them.
    - Publish the `ProductStockDeducted` event using Wolverine's `IMessageBus`.
    - If insufficient, publish the `ProductStockDeductionFailed` event.
- [ ] T011: **Update Product Consumer**: In `SaleProducts.Consumer`, modify the handler for `OrderPlaced` to dispatch the `DeductStockCommand` using MediatR's `ISender`.
- [ ] T012: **Create Order Success Handler**: In `SaleOrders.Consumer`, create a new handler for the `ProductStockDeducted` event. This handler will:
    - Load the `Order` aggregate.
    - Update the order's status to `Allocated`.
    - Save the `Order` aggregate.
- [ ] T013: **Create Order Failure Handler**: In `SaleOrders.Consumer`, create a new handler for the `ProductStockDeductionFailed` event. This handler will:
    - Load the `Order` aggregate.
    - Update the order's status to `Failed`.
    - Save the `Order` aggregate.

## Phase 3.4: Polish
- [ ] T014 [P]: **Unit Tests**: Add unit tests for the `DeductStockCommandHandler` logic, mocking dependencies where appropriate.
- [ ] T015 [P]: **Logging**: Add structured logging to all new handlers and command handlers to provide visibility into the process.
- [ ] T016: **Code Review & Refactor**: Review all new code for clarity, consistency, and adherence to project conventions.

## Dependencies
- **T001-T004** (Setup) must be completed before all other tasks.
- **T005-T008** (Tests) must be completed before **T009-T013** (Implementation).
- **T009** must be completed before **T010**.
- **T010** must be completed before **T011**.
- **T009-T013** must be completed before **T014-T016** (Polish).

## Parallel Example
The following test creation tasks can be run in parallel:
```
Task: "T005: Integration Test (Product Stock Deduction)"
Task: "T007: Integration Test (Order Status Update - Success)"
```
Once the initial tests are created, their failure cases can also be added in parallel:
```
Task: "T006: Integration Test (Product Stock Failure)"
Task: "T008: Integration Test (Order Status Update - Failure)"
```

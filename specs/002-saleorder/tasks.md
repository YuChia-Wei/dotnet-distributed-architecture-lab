# Tasks: Cancel Sale Order

**Input**: Design documents from `/specs/002-saleorder/`
**Prerequisites**: plan.md, data-model.md, contracts/, quickstart.md

## Phase 3.1: Setup
- [ ] T001 No new setup tasks required.

## Phase 3.2: Domain and Contract Updates
- [ ] T002 [P] Update `Order` entity in `src/Order/DomainCore/SaleOrders.Domains/Order.cs` to include `Status` property and `Cancel()` method as per `data-model.md`.
- [ ] T003 [P] Define the `OrderCancelled` integration event in `src/BC-Contracts/Lab.MessageSchemas.Orders/IntegrationEvents/OrderCancelled.cs` as per `contracts/OrderCancelled.cs`.

## Phase 3.3: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.4
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T004 [P] Create unit tests for the `Order.Cancel()` method in a new file `tests/SaleOrders.Domains.Tests/OrderTests.cs`.
- [ ] T005 [P] Create integration tests for the `PATCH /api/orders/{orderId}/cancel` endpoint in a new file `tests/SaleOrders.Tests/CancelOrderTests.cs`. This test should verify that the order status is updated and that an `OrderCancelled` event is published.

## Phase 3.4: Core Implementation (ONLY after tests are failing)
- [ ] T006 Create the `CancelOrder` command and its handler in `src/Order/DomainCore/SaleOrders.Applications/Commands/CancelOrder.cs`.
- [ ] T007 Implement the `CancelOrder` handler to use Marten for saving the updated order and Wolverine for publishing the `OrderCancelled` event.
- [ ] T008 Add the `PATCH /api/orders/{orderId}/cancel` endpoint to `OrdersController` in `src/Order/Presentation/SaleOrders.WebApi/Controllers/OrdersController.cs`.

## Phase 3.5: Polish
- [ ] T009 [P] Add XML comments to all new public methods and properties.

## Dependencies
- T002 and T003 can be done in parallel.
- T004 and T005 must be done before T006, T007, and T008.
- T006 must be done before T007 and T008.

## Parallel Example
```
# Launch T002-T005 together:
Task: "Update `Order` entity in `src/Order/DomainCore/SaleOrders.Domains/Order.cs`"
Task: "Define the `OrderCancelled` integration event in `src/BC-Contracts/Lab.MessageSchemas.Orders/IntegrationEvents/OrderCancelled.cs`"
Task: "Create unit tests for the `Order.Cancel()` method in a new file `tests/SaleOrders.Domains.Tests/OrderTests.cs`"
Task: "Create integration tests for the `PATCH /api/orders/{orderId}/cancel` endpoint in a new file `tests/SaleOrders.Tests/CancelOrderTests.cs`"
```

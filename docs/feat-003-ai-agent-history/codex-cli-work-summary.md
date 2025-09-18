```terminaloutput
> - Added the shared order-details contract so both contexts can agree on the payload shape (src/BC-Contracts/Lab.MessageSchemas.Orders/DataTransferObjects/
  OrderDetailsResponse.cs:1).
  - Built the GetOrderDetailsQuery + handler and exposed /api/orders/{orderId} from the Orders API, including DI wiring for handler discovery (src/Order/DomainCore/
  SaleOrders.Applications/Queries/GetOrderDetails.cs:1, src/Order/Presentation/SaleOrders.WebApi/Controllers/OrdersController.cs:37, src/Order/DomainCore/
  SaleOrders.Applications/ServiceCollectionExtensions.cs:8, src/Order/Presentation/SaleOrders.WebApi/Program.cs:122).
  - Extended the product domain with a Restock operation and a dedicated command handler to raise stock levels safely (src/Product/DomainCore/SaleProducts.Domains/
  Product.cs:69, src/Product/DomainCore/SaleProducts.Applications/Commands/RestockProduct.cs:6, tests/SaleProducts.Domains.Tests/ProductTests.cs:60).
  - Introduced an HTTP client plus idempotency store so the consumer can query order details and skip duplicate cancellations; both are registered with DI and backed
  by an auto-created table (src/Product/DomainCore/SaleProducts.Infrastructure/Clients/OrderApiClient.cs:1, src/Product/DomainCore/SaleProducts.Infrastructure/
  Repositories/OrderCancellationHistoryRepository.cs:8, src/Product/DomainCore/SaleProducts.Infrastructure/ServiceCollectionExtensions.cs:17, src/
  Product/DomainCore/SaleProducts.Infrastructure/SaleProducts.Infrastructure.csproj:10, src/Product/DomainCore/SaleProducts.Applications/Repositories/
  IOrderCancellationHistoryRepository.cs:3).
  - Implemented OrderCancelledHandler to call the Orders API, filter bad line items, dispatch restock commands, and log/idempotently complete the workflow (src/Product/
  Presentation/SaleProducts.Consumer/IntegrationEventHandlers/OrderCancelledHandler.cs:10).
  - Added end-to-end coverage: web API test that exercises the new endpoint with a mocked bus and an integration test that drives the consumer through a cancellation
  (tests/SaleOrders.Tests/GetOrderDetailsEndpointTests.cs:18, tests/SaleProducts.Tests/OrderCancellationStockRestorationTests.cs:21).
  - Updated docker compose to pass the Orders API base address to the product-consumer container, with a matching default fallback in code (docker-compose/docker-
  compose.yml:220, src/Product/DomainCore/SaleProducts.Infrastructure/ServiceCollectionExtensions.cs:27).

  Tests run:

  - dotnet test tests/SaleOrders.Tests/SaleOrders.Tests.csproj
  - dotnet test tests/SaleProducts.Tests/SaleProducts.Tests.csproj
  - dotnet test (fails because SaleOrders.Domains.Tests is missing DiffEngine.dll and SaleProducts.Domains.Tests is missing Confluent.Kafka.dll in this environment)

  Manual quickstart validation (T017) was not executed. Suggested follow-ups:

  1. Restore the missing DiffEngine and Confluent.Kafka packages so the domain suites run cleanly.
  2. Set Services__Orders__BaseAddress appropriately in non-docker environments.
  3. Walk through specs/003-product-consumer-ordercancelled/quickstart.md once the stack is up to confirm the full cancellation workflow.
```
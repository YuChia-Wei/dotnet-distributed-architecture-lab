using JasperFx.Core.Reflection;
using Lab.BuildingBlocks.Integrations;
using Lab.BoundedContextContracts.Orders.IntegrationEvents;
using Lab.BoundedContextContracts.Products.IntegrationEvents;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Moq;
using SaleProducts.Applications;
using SaleProducts.Applications.Repositories;
using SaleProducts.Consumer.IntegrationEventHandlers;
using SaleProducts.Domains;
using SaleProducts.Infrastructure;
using Shouldly;
using Wolverine;
using Wolverine.Tracking;
using ServiceCollectionExtensions = SaleProducts.Applications.ServiceCollectionExtensions;

namespace SaleProducts.Tests;

public class StockDeductionIntegrationTests
{
    [Fact]
    public async Task when_order_placed_and_stock_is_sufficient_then_stock_deducted_event_is_published()
    {
        // Arrange
        var orderId = Guid.NewGuid();
        var productId = Guid.NewGuid();
        var orderPlaced = new OrderPlaced(orderId, productId, "Test Product", 10);

        var configuration = new ConfigurationRoot(new List<IConfigurationProvider>());

        var productRepositoryMock = new Mock<IProductDomainRepository>();
        // Setup mock if needed for the handler
        var valueFunction = new Product("test-product", "test-description", 10m, 10);
        productRepositoryMock.Setup(x => x.GetByIdAsync(productId))
                             .ReturnsAsync(valueFunction);

        using var host = await Host.CreateDefaultBuilder()
                                   .UseWolverine(opts =>
                                   {
                                       opts.StubAllExternalTransports();

                                       // 全部走本機，不碰外部 broker
                                       opts.PublishMessage<IIntegrationEvent>()
                                           .ToLocalQueue("integration-events");

                                       opts.Discovery.IncludeAssembly(typeof(InventoryDeductionOnOrderPlacedHandler).Assembly);
                                       opts.Discovery.IncludeAssembly(typeof(ServiceCollectionExtensions).Assembly);
                                       opts.Services.AddApplicationServices();
                                       opts.Services.AddInfrastructureServices(configuration);
                                       opts.Services.AddSingleton(productRepositoryMock.Object);
                                   }).StartAsync();

        // Act
        var session = await host.InvokeMessageAndWaitAsync(orderPlaced);

        // Assert
        // 因為沒有 mock ProductStockDeducted handler，所以這邊要從 no routes 的清單中找發送過的 message
        var message = session.NoRoutes.SingleMessage<ProductStockDeducted>();
        message.ShouldBeOfType<ProductStockDeducted>();
        message.As<ProductStockDeducted>().OrderId.ShouldBe(orderId);
    }
}
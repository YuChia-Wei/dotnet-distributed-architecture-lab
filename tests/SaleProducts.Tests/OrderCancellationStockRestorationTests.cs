using Lab.BuildingBlocks.Integrations;
using Lab.MessageSchemas.Orders.IntegrationEvents;
using Lab.MessageSchemas.Orders.DataTransferObjects;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Moq;
using SaleProducts.Applications;
using SaleProducts.Applications.Repositories;
using SaleProducts.Consumer.IntegrationEventHandlers;
using SaleProducts.Domains;
using SaleProducts.Infrastructure;
using SaleProducts.Infrastructure.Clients;
using Shouldly;
using Wolverine;
using Wolverine.Tracking;
using ServiceCollectionExtensions = SaleProducts.Applications.ServiceCollectionExtensions;

namespace SaleProducts.Tests;

public class OrderCancellationStockRestorationTests
{
    [Fact]
    public async Task when_order_cancelled_then_stock_is_restored()
    {
        // Arrange
        var orderId = Guid.NewGuid();
        var productId = Guid.NewGuid();
        var initialStock = 3;
        var restockQuantity = 2;
        var configuration = new ConfigurationRoot(new List<IConfigurationProvider>());

        var product = new Product("test-product", "test-description", 10m, initialStock);

        var repositoryMock = new Mock<IProductDomainRepository>();
        repositoryMock.Setup(repo => repo.GetByIdAsync(productId))
                      .ReturnsAsync(product);
        repositoryMock.Setup(repo => repo.UpdateAsync(It.IsAny<Product>()))
                      .Returns(Task.CompletedTask);

        var orderDetailsResponse = new OrderDetailsResponse
        {
            OrderId = orderId,
            LineItems =
            [
                new LineItemDto
                {
                    ProductId = productId,
                    Quantity = restockQuantity,
                },
            ],
        };

        var orderApiClientMock = new Mock<IOrderApiClient>();
        orderApiClientMock.Setup(client => client.GetOrderDetailsAsync(orderId))
                          .ReturnsAsync(orderDetailsResponse);

        var historyRepositoryMock = new Mock<IOrderCancellationHistoryRepository>();
        historyRepositoryMock.Setup(repo => repo.HasProcessedAsync(orderId))
                             .ReturnsAsync(false);
        historyRepositoryMock.Setup(repo => repo.MarkProcessedAsync(orderId))
                             .Returns(Task.CompletedTask);

        using var host = await Host.CreateDefaultBuilder()
                                   .UseWolverine(opts =>
                                   {
                                       opts.StubAllExternalTransports();
                                       opts.PublishMessage<IIntegrationEvent>()
                                           .ToLocalQueue("integration-events");
                                       opts.Discovery.IncludeAssembly(typeof(InventoryDeductionOnOrderPlacedHandler).Assembly);
                                       opts.Discovery.IncludeAssembly(typeof(ServiceCollectionExtensions).Assembly);
                                       opts.Services.AddApplicationServices();
                                       opts.Services.AddInfrastructureServices(configuration);
                                       opts.Services.AddSingleton<IOrderApiClient>(orderApiClientMock.Object);
                                       opts.Services.AddSingleton<IOrderCancellationHistoryRepository>(historyRepositoryMock.Object);
                                       opts.Services.AddSingleton<IProductDomainRepository>(repositoryMock.Object);
                                   }).StartAsync();

        // Act
        await host.InvokeMessageAndWaitAsync(new OrderCancelled(orderId));

        // Assert
        repositoryMock.Verify(repo => repo.GetByIdAsync(productId), Times.Once);
        repositoryMock.Verify(repo => repo.UpdateAsync(It.Is<Product>(p => p.Stock == initialStock + restockQuantity)), Times.Once);
        product.Stock.ShouldBe(initialStock + restockQuantity);
        historyRepositoryMock.Verify(repo => repo.MarkProcessedAsync(orderId), Times.Once);
    }
}

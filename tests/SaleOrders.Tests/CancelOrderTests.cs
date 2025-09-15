using JasperFx.Core.Reflection;
using Lab.BuildingBlocks.Integrations;
using Lab.MessageSchemas.Orders.IntegrationEvents;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Moq;
using SaleOrders.Applications;
using SaleOrders.Applications.Commands;
using SaleOrders.Applications.Repositories;
using SaleOrders.Domains;
using SaleOrders.Infrastructure;
using Shouldly;
using Wolverine;
using Wolverine.Tracking;

namespace SaleOrders.Tests;

public class CancelOrderTests
{
    [Fact]
    public async Task when_cancel_order_then_status_updated_and_event_published()
    {
        // Arrange
        var order = new Order(DateTime.UtcNow, 100m, Guid.NewGuid(), "P", 1);
        var orderId = order.Id;

        var configuration = new ConfigurationRoot(new List<IConfigurationProvider>());

        var orderRepositoryMock = new Mock<IOrderDomainRepository>();
        orderRepositoryMock.Setup(x => x.GetByIdAsync(orderId, It.IsAny<CancellationToken>()))
                           .ReturnsAsync(order);

        orderRepositoryMock.Setup(x => x.UpdateAsync(It.IsAny<Order>(), It.IsAny<CancellationToken>()))
                           .Returns(Task.CompletedTask);

        using var host = await Host.CreateDefaultBuilder()
                                   .UseWolverine(opts =>
                                   {
                                       opts.StubAllExternalTransports();

                                       // route integration events to in-memory queue
                                       opts.PublishMessage<IIntegrationEvent>()
                                           .ToLocalQueue("integration-events");

                                       // discover handlers/DI
                                       opts.Discovery.IncludeAssembly(typeof(SaleOrders.Applications.ServiceCollectionExtensions).Assembly);

                                       // register app services
                                       opts.Services.AddApplicationServices();
                                       opts.Services.AddInfrastructureServices(configuration);

                                       // override repository with mock
                                       opts.Services.AddSingleton(orderRepositoryMock.Object);
                                   }).StartAsync();

        // Act
        var session = await host.InvokeMessageAndWaitAsync(new CancelOrder(orderId));

        // Assert
        order.Status.ShouldBe(OrderStatus.Cancelled);
        orderRepositoryMock.Verify(r => r.UpdateAsync(It.Is<Order>(o => o.Id == orderId), It.IsAny<CancellationToken>()), Times.Once);

        var message = session.NoRoutes.SingleMessage<OrderCancelled>();
        message.ShouldBeOfType<OrderCancelled>();
        message.As<OrderCancelled>().OrderId.ShouldBe(orderId);
    }
}

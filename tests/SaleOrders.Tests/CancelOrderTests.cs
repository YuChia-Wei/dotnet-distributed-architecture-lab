using JasperFx.Core.Reflection;
using Lab.BuildingBlocks.Integrations;
using Lab.BoundedContextContracts.Orders.IntegrationEvents;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Moq;
using SaleOrders.Applications;
using SaleOrders.Applications.Repositories;
using SaleOrders.Applications.UseCases;
using SaleOrders.Domains;
using SaleOrders.Infrastructure;
using Shouldly;
using Wolverine;

namespace SaleOrders.Tests;

/// <summary>
/// 驗證取消訂單 use case 的行為測試。
/// </summary>
public class CancelOrderTests
{
    /// <summary>
    /// 驗證取消訂單後會更新訂單狀態並發布事件。
    /// </summary>
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
        using var scope = host.Services.CreateScope();
        var useCase = scope.ServiceProvider.GetRequiredService<ICancelOrderUseCase>();
        await useCase.ExecuteAsync(new CancelOrderInput(orderId));

        // Assert
        order.Status.ShouldBe(OrderStatus.Cancelled);
        orderRepositoryMock.Verify(r => r.UpdateAsync(It.Is<Order>(o => o.Id == orderId), It.IsAny<CancellationToken>()), Times.Once);

    }
}

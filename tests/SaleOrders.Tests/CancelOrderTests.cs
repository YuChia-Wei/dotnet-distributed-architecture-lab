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

        var committerMock = new Mock<IOrderEventCommitter>();
        committerMock.Setup(x => x.CommitAsync(
                                It.IsAny<Order>(),
                                It.IsAny<IReadOnlyCollection<IIntegrationEvent>>(),
                                It.IsAny<CancellationToken>()))
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
                                       opts.Services.AddSingleton(committerMock.Object);
                                   }).StartAsync();

        // Act
        using var scope = host.Services.CreateScope();
        var useCase = scope.ServiceProvider.GetRequiredService<ICancelOrderUseCase>();
        await useCase.ExecuteAsync(new CancelOrderInput(orderId, "customer request"));

        // Assert
        order.Status.ShouldBe(OrderStatus.Cancelled);
        committerMock.Verify(
            c => c.CommitAsync(
                It.Is<Order>(o => o.Id == orderId),
                It.Is<IReadOnlyCollection<IIntegrationEvent>>(events =>
                    events.Count == 1 &&
                    events.Single().GetType() == typeof(OrderCancelled) &&
                    ((OrderCancelled)events.Single()).Reason == "customer request"),
                It.IsAny<CancellationToken>()),
            Times.Once);
    }

    /// <summary>驗證重複取消是 no-op，不會再次寫入事件或 outbox。</summary>
    [Fact]
    public async Task given_cancelled_order_when_cancelled_again_then_commit_is_skipped()
    {
        var order = new Order(DateTime.UtcNow, 100m, Guid.NewGuid(), "P", 1);
        order.Cancel("initial cancellation");
        order.MarkChangesAsCommitted(2);

        var repositoryMock = new Mock<IOrderDomainRepository>();
        repositoryMock.Setup(x => x.GetByIdAsync(order.Id, It.IsAny<CancellationToken>()))
                      .ReturnsAsync(order);
        var committerMock = new Mock<IOrderEventCommitter>(MockBehavior.Strict);
        var useCase = new CancelOrderUseCase(repositoryMock.Object, committerMock.Object);

        await useCase.ExecuteAsync(new CancelOrderInput(order.Id, "duplicate request"));

        order.Status.ShouldBe(OrderStatus.Cancelled);
        order.DomainEvents.ShouldBeEmpty();
        committerMock.VerifyNoOtherCalls();
    }
}

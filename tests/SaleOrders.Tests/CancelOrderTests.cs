using JasperFx.Core.Reflection;
using Lab.BuildingBlocks.Integrations;
using Lab.BoundedContextContracts.Orders.IntegrationEvents;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using NSubstitute;
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

        var orderRepository = Substitute.For<IOrderDomainRepository>();
        orderRepository.FindByIdAsync(orderId, Arg.Any<CancellationToken>()).Returns(order);

        var committer = Substitute.For<IOrderEventCommitter>();

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
                                       opts.Services.AddSingleton(orderRepository);
                                       opts.Services.AddSingleton(committer);
                                   }).StartAsync();

        // Act
        using var scope = host.Services.CreateScope();
        var useCase = scope.ServiceProvider.GetRequiredService<ICancelOrderUseCase>();
        await useCase.ExecuteAsync(new CancelOrderInput(orderId, "customer request"), CancellationToken.None);

        // Assert
        order.Status.ShouldBe(OrderStatus.Cancelled);
        await committer.Received(1).CommitAsync(
                Arg.Is<Order>(o => o.Id == orderId),
                Arg.Is<IReadOnlyCollection<IIntegrationEvent>>(events =>
                    events.Count == 1 &&
                    events.Single().GetType() == typeof(OrderCancelled) &&
                    ((OrderCancelled)events.Single()).Reason == "customer request"),
                Arg.Any<CancellationToken>());
    }

    /// <summary>驗證重複取消是 no-op，不會再次寫入事件或 outbox。</summary>
    [Fact]
    public async Task given_cancelled_order_when_cancelled_again_then_commit_is_skipped()
    {
        var order = new Order(DateTime.UtcNow, 100m, Guid.NewGuid(), "P", 1);
        order.Cancel("initial cancellation");
        order.MarkChangesAsCommitted(2);

        var repository = Substitute.For<IOrderDomainRepository>();
        repository.FindByIdAsync(order.Id, Arg.Any<CancellationToken>()).Returns(order);
        var committer = Substitute.For<IOrderEventCommitter>();
        var useCase = new CancelOrderUseCase(repository, committer);

        await useCase.ExecuteAsync(new CancelOrderInput(order.Id, "duplicate request"), CancellationToken.None);

        order.Status.ShouldBe(OrderStatus.Cancelled);
        order.DomainEvents.ShouldBeEmpty();
        await committer.DidNotReceiveWithAnyArgs().CommitAsync(default!, default!, default);
    }
}

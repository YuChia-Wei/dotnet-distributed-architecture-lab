using System;
using System.Threading.Tasks;
using Lab.MessageSchemas.Orders.IntegrationEvents;
using Lab.MessageSchemas.Products.IntegrationEvents;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using SaleProducts.Applications;
using SaleProducts.Infrastructure;
using Shouldly;
using Wolverine;
using Wolverine.Tracking;
using Xunit;
using Microsoft.Extensions.Configuration;
using Moq;
using SaleProducts.Applications.Repositories;
using System.Collections.Generic;
using System.Linq;
using JasperFx.Core.Reflection;

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

        using var host = await Host.CreateDefaultBuilder()
            .UseWolverine(opts =>
            {
                opts.Discovery.IncludeAssembly(typeof(SaleProducts.Consumer.Program).Assembly);
                opts.Services.AddApplicationServices();
                opts.Services.AddInfrastructureServices(configuration);
                opts.Services.AddSingleton(productRepositoryMock.Object);
            }).StartAsync();

        var runtime = host.Services.GetRequiredService<Wolverine.IWolverineRuntime>();
        var handlers = runtime.Handlers.KnownHandlers();
        var orderPlacedHandler = handlers.FirstOrDefault(x => x.MessageType == typeof(OrderPlaced));


        // Act
        var session = await host.InvokeMessageAndWaitAsync(orderPlaced);

        // Assert
        var envelope = session.Sent.SingleEnvelope<ProductStockDeducted>();
        envelope.Message.OrderId.ShouldBe(orderId);
    }
}

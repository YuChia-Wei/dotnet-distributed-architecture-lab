using System.Net;
using System.Collections.Generic;
using System.Net.Http.Json;
using System.Threading;
using Lab.MessageSchemas.Orders.DataTransferObjects;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Moq;
using SaleOrders.Applications.Queries;
using Shouldly;
using Wolverine;

namespace SaleOrders.Tests;

public class GetOrderDetailsEndpointTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;

    public GetOrderDetailsEndpointTests(WebApplicationFactory<Program> factory)
    {
        this._factory = factory;
    }

    [Fact]
    public async Task when_getting_order_details_then_returns_expected_payload()
    {
        // Arrange
        var orderId = Guid.NewGuid();
        var expected = new OrderDetailsResponse
        {
            OrderId = orderId,
            LineItems =
            [
                new LineItemDto
                {
                    ProductId = Guid.NewGuid(),
                    Quantity = 3,
                },
            ],
        };

        var messageBusMock = new Mock<IMessageBus>();
        messageBusMock.Setup(bus => bus.InvokeAsync<OrderDetailsResponse>(It.Is<GetOrderDetailsQuery>(query => query.OrderId == orderId), It.IsAny<CancellationToken>(), It.IsAny<TimeSpan?>()))
                      .ReturnsAsync(expected);

        var client = this._factory.WithWebHostBuilder(builder =>
        {
            builder.UseSetting("QUEUE_SERVICE", "Kafka");
            builder.UseSetting("ConnectionStrings:KafkaBroker", "localhost:9092");
            builder.ConfigureAppConfiguration((_, config) =>
            {
                config.AddInMemoryCollection(new Dictionary<string, string?>
                {
                    ["QUEUE_SERVICE"] = "Kafka",
                    ["ConnectionStrings:KafkaBroker"] = "localhost:9092",
                });
            });
            builder.ConfigureTestServices(services =>
            {
                services.RemoveAll<IMessageBus>();
                services.AddSingleton(messageBusMock.Object);
            });
        }).CreateClient();

        // Act
        var response = await client.GetAsync($"/api/orders/{orderId}");

        // Assert
        response.StatusCode.ShouldBe(HttpStatusCode.OK);
        var payload = await response.Content.ReadFromJsonAsync<OrderDetailsResponse>();
        payload.ShouldNotBeNull();
        payload!.OrderId.ShouldBe(expected.OrderId);
        payload.LineItems.Count.ShouldBe(expected.LineItems.Count);
        payload.LineItems[0].ShouldBe(expected.LineItems[0]);
        messageBusMock.Verify(bus => bus.InvokeAsync<OrderDetailsResponse>(It.IsAny<GetOrderDetailsQuery>(), It.IsAny<CancellationToken>(), It.IsAny<TimeSpan?>()), Times.Once);
    }
}

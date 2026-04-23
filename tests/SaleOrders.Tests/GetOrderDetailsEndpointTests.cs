using System.Net;
using System.Collections.Generic;
using System.Net.Http.Json;
using System.Threading;
using Lab.BoundedContextContracts.Orders.DataTransferObjects;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Moq;
using SaleOrders.Applications.UseCases;
using Shouldly;

namespace SaleOrders.Tests;

/// <summary>
/// 驗證取得訂單明細端點的整合測試。
/// </summary>
public class GetOrderDetailsEndpointTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;

    /// <summary>
    /// 初始化取得訂單明細端點測試。
    /// </summary>
    /// <param name="factory">Web 應用程式測試工廠。</param>
    public GetOrderDetailsEndpointTests(WebApplicationFactory<Program> factory)
    {
        this._factory = factory;
    }

    /// <summary>
    /// 驗證取得訂單明細端點會回傳預期內容。
    /// </summary>
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

        var useCaseMock = new Mock<IGetOrderDetailsUseCase>();
        useCaseMock.Setup(useCase => useCase.ExecuteAsync(It.Is<GetOrderDetailsInput>(input => input.OrderId == orderId), It.IsAny<CancellationToken>()))
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
                services.RemoveAll<IGetOrderDetailsUseCase>();
                services.AddSingleton(useCaseMock.Object);
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
        useCaseMock.Verify(useCase => useCase.ExecuteAsync(It.IsAny<GetOrderDetailsInput>(), It.IsAny<CancellationToken>()), Times.Once);
    }
}

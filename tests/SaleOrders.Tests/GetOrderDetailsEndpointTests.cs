using System.Net;
using System.Collections.Generic;
using System.Net.Http.Json;
using System.Threading;
using Lab.BoundedContextContracts.Orders.DataTransferObjects;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Microsoft.Extensions.Logging;
using NSubstitute;
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

        var useCase = Substitute.For<IGetOrderDetailsUseCase>();
        useCase.ExecuteAsync(
                   Arg.Is<GetOrderDetailsInput>(input => input.OrderId == orderId),
                   Arg.Any<CancellationToken>())
               .Returns(expected);

        var client = this._factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureLogging(logging => logging.ClearProviders());
            builder.UseSetting("QUEUE_SERVICE", "InMemory");
            builder.UseSetting("Messaging:OutboxRelay:Enabled", "false");
            builder.ConfigureAppConfiguration((_, config) =>
            {
                config.AddInMemoryCollection(new Dictionary<string, string?>
                {
                    ["QUEUE_SERVICE"] = "InMemory",
                    ["Messaging:OutboxRelay:Enabled"] = "false",
                });
            });
            builder.ConfigureTestServices(services =>
            {
                services.RemoveAll<IGetOrderDetailsUseCase>();
                services.AddSingleton(useCase);
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
        await useCase.Received(1).ExecuteAsync(
            Arg.Any<GetOrderDetailsInput>(),
            Arg.Any<CancellationToken>());
    }
}

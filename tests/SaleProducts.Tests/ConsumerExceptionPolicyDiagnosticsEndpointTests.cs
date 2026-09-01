using System.Net;
using System.Net.Http.Json;
using Lab.BuildingBlocks.Integrations.Diagnostics;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Moq;
using SaleProducts.Applications.UseCases;
using SaleProducts.WebApi.Models.Responses;
using Shouldly;

namespace SaleProducts.Tests;

public sealed class ConsumerExceptionPolicyDiagnosticsEndpointTests(
    WebApplicationFactory<Program> factory) : IClassFixture<WebApplicationFactory<Program>>
{
    [Fact]
    public async Task given_an_enabled_probe_when_timeout_is_requested_then_the_endpoint_returns_accepted()
    {
        var probeId = Guid.CreateVersion7();
        var useCase = new Mock<ITriggerConsumerExceptionPolicyProbeUseCase>();
        useCase.Setup(candidate => candidate.ExecuteAsync(
                       It.Is<TriggerConsumerExceptionPolicyProbeInput>(input =>
                           input.FailureKind == ConsumerExceptionPolicyProbeFailureKind.Timeout),
                       It.IsAny<CancellationToken>()))
               .ReturnsAsync(new TriggerConsumerExceptionPolicyProbeOutput(
                   TriggerConsumerExceptionPolicyProbeStatus.Accepted,
                   probeId,
                   ConsumerExceptionPolicyProbeFailureKind.Timeout));
        var client = CreateClient(useCase.Object);

        var response = await client.PostAsync(
            "/api/products/diagnostics/consumer-exception-policy/timeout",
            new StringContent(string.Empty));

        response.StatusCode.ShouldBe(HttpStatusCode.Accepted);
        var payload = await response.Content.ReadFromJsonAsync<ConsumerExceptionPolicyProbeResponse>();
        payload.ShouldNotBeNull();
        payload.ProbeId.ShouldBe(probeId);
        payload.FailureKind.ShouldBe(nameof(ConsumerExceptionPolicyProbeFailureKind.Timeout));
        payload.Topic.ShouldBe("products.integration.events");
        payload.Consumer.ShouldBe("orders-consumer");
    }

    [Fact]
    public async Task given_a_disabled_probe_when_triggered_then_the_endpoint_returns_not_found()
    {
        var useCase = new Mock<ITriggerConsumerExceptionPolicyProbeUseCase>();
        useCase.Setup(candidate => candidate.ExecuteAsync(
                       It.IsAny<TriggerConsumerExceptionPolicyProbeInput>(),
                       It.IsAny<CancellationToken>()))
               .ReturnsAsync(new TriggerConsumerExceptionPolicyProbeOutput(
                   TriggerConsumerExceptionPolicyProbeStatus.Disabled,
                   null,
                   ConsumerExceptionPolicyProbeFailureKind.Unhandled));
        var client = CreateClient(useCase.Object);

        var response = await client.PostAsync(
            "/api/products/diagnostics/consumer-exception-policy/unhandled",
            new StringContent(string.Empty));

        response.StatusCode.ShouldBe(HttpStatusCode.NotFound);
    }

    [Fact]
    public async Task given_an_unknown_failure_kind_when_triggered_then_the_endpoint_returns_bad_request()
    {
        var useCase = new Mock<ITriggerConsumerExceptionPolicyProbeUseCase>();
        var client = CreateClient(useCase.Object);

        var response = await client.PostAsync(
            "/api/products/diagnostics/consumer-exception-policy/not-supported",
            new StringContent(string.Empty));

        response.StatusCode.ShouldBe(HttpStatusCode.BadRequest);
        useCase.VerifyNoOtherCalls();
    }

    private HttpClient CreateClient(ITriggerConsumerExceptionPolicyProbeUseCase useCase)
        => factory.WithWebHostBuilder(builder =>
        {
            builder.UseSetting("QUEUE_SERVICE", "InMemory");
            builder.ConfigureAppConfiguration((_, configuration) =>
            {
                configuration.AddInMemoryCollection(new Dictionary<string, string?>
                {
                    ["QUEUE_SERVICE"] = "InMemory",
                    [ConsumerExceptionPolicyProbeOptions.EnabledConfigurationKey] = "true",
                });
            });
            builder.ConfigureTestServices(services =>
            {
                services.RemoveAll<ITriggerConsumerExceptionPolicyProbeUseCase>();
                services.AddSingleton(useCase);
            });
        }).CreateClient();
}

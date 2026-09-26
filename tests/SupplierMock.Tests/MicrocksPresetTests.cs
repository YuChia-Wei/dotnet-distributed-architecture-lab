using System.Net;
using System.Text.Json;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Hosting.Server;
using Microsoft.AspNetCore.Hosting.Server.Features;
using Microsoft.Extensions.DependencyInjection;

public sealed class MicrocksPresetTests : IAsyncLifetime
{
    private WebApplication? native;
    private HttpClient? client;
    private MicrocksPresetController? controller;
    private readonly List<string> uploadedNames = [];
    private string nativeMode = "unconfigured";
    private bool rejectUpload;
    private int uploads;

    [Fact]
    [Trait("Scenario", "M02-invalid-mode")]
    public async Task Given_invalid_mode_When_checked_Then_no_native_upload_occurs()
    {
        await GivenNativeMicrocksAsync();
        var valid = MicrocksPresetController.IsValidMode("http://evil.test/");
        var failure = await Record.ExceptionAsync(() => controller!.ChangeAsync("../proxy", TestContext.Current.CancellationToken));
        ThenInvalidModeIsRejectedWithoutUpload(valid, failure);
    }

    [Fact]
    [Trait("Scenario", "M02-unconfigured-custom")]
    public async Task Given_unconfigured_or_native_custom_service_When_state_is_read_Then_mode_is_not_claimed()
    {
        await GivenNativeMicrocksAsync();
        var unconfigured = await WhenReadingStateAsync();
        ThenUnconfiguredHasNoMode(unconfigured);
        nativeMode = "custom";
        var custom = await WhenReadingStateAsync();
        ThenCustomHasNoMode(custom);
    }

    [Fact]
    [Trait("Scenario", "M02-proxy-readback")]
    public async Task Given_native_service_When_proxy_preset_is_uploaded_Then_filename_and_all_dispatchers_are_verified()
    {
        await GivenNativeMicrocksAsync();
        var selected = await WhenSelectingProxyAsync();
        ThenProxyReadbackMatchesNative(selected);
        nativeMode = "custom";
        var externalEdit = await WhenReadingStateAsync();
        ThenCustomHasNoMode(externalEdit);
    }

    [Fact]
    [Trait("Scenario", "M02-upstream-failure")]
    public async Task Given_failed_native_upload_When_selecting_proxy_Then_failed_state_allows_explicit_retry()
    {
        await GivenNativeMicrocksAsync();
        rejectUpload = true;
        var failure = await Record.ExceptionAsync(WhenSelectingProxyAsync);
        var failedState = await WhenReadingStateAsync();
        ThenFailureIsTruthful(failure, failedState);
        rejectUpload = false;
        var recovered = await WhenSelectingProxyAsync();
        ThenProxyReadbackMatchesNative(recovered);
    }

    private async Task GivenNativeMicrocksAsync()
    {
        var builder = WebApplication.CreateBuilder();
        builder.WebHost.UseUrls("http://127.0.0.1:0");
        native = builder.Build();
        native.MapGet("/api/services", () => nativeMode switch
        {
            "unconfigured" => Results.Json(Array.Empty<object>()),
            "proxy" => Results.Json(new[] { new { id = "supplier-1", name = "Supplier API", version = "1.0.0", operations = ProxyOperations() } }),
            _ => Results.Json(new[] { new { id = "supplier-1", name = "Supplier API", version = "1.0.0", operations = new[]
            {
                new { name = "GET /supplier/catalog/{sku}", method = "GET", dispatcher = "PROXY", dispatcherRules = "http://changed-upstream:8080/" }
            } } })
        });
        native.MapPost("/api/artifact/upload", async (HttpRequest request) =>
        {
            uploads++;
            if (rejectUpload) return Results.StatusCode(503);
            var form = await request.ReadFormAsync();
            var file = Assert.Single(form.Files);
            uploadedNames.Add(file.FileName);
            using var reader = new StreamReader(file.OpenReadStream());
            var artifact = await reader.ReadToEndAsync();
            Assert.Contains("Supplier API", artifact);
            nativeMode = artifact.Contains("proxy each imported operation", StringComparison.Ordinal) ? "proxy" : "custom";
            return Results.Ok(new { imported = true });
        });
        await native.StartAsync();
        var address = native.Services.GetRequiredService<IServer>().Features.Get<IServerAddressesFeature>()!.Addresses.Single();
        client = new HttpClient { BaseAddress = new Uri(address), Timeout = TimeSpan.FromSeconds(35) };
        controller = new MicrocksPresetController(client, Path.Combine(AppContext.BaseDirectory, "microcks"));
    }

    private static object[] ProxyOperations() =>
    [
        new { name = "GET /supplier/catalog/{sku}", method = "GET", dispatcher = "PROXY", dispatcherRules = "http://supplier-sandbox:8080/" },
        new { name = "POST /supplier/orders", method = "POST", dispatcher = "PROXY", dispatcherRules = "http://supplier-sandbox:8080/" },
        new { name = "GET /supplier/orders/by-client-request/{clientRequestId}", method = "GET", dispatcher = "PROXY", dispatcherRules = "http://supplier-sandbox:8080/" }
    ];

    private Task<MicrocksState> WhenReadingStateAsync() => controller!.GetStateAsync();
    private Task<MicrocksState> WhenSelectingProxyAsync() => controller!.ChangeAsync("proxy");

    private void ThenInvalidModeIsRejectedWithoutUpload(bool valid, Exception? failure)
    {
        Assert.False(valid);
        Assert.IsType<ArgumentException>(failure);
        Assert.Equal(0, uploads);
    }

    private static void ThenUnconfiguredHasNoMode(MicrocksState state)
    {
        Assert.Equal("unconfigured", state.Status);
        Assert.Null(state.Mode);
        Assert.Null(state.ServiceId);
    }

    private static void ThenCustomHasNoMode(MicrocksState state)
    {
        Assert.Equal("custom", state.Status);
        Assert.Null(state.Mode);
        Assert.Equal("supplier-1", state.ServiceId);
        Assert.NotEmpty(state.Operations);
    }

    private void ThenProxyReadbackMatchesNative(MicrocksState state)
    {
        Assert.Equal("ready", state.Status);
        Assert.Equal("proxy", state.Mode);
        Assert.Equal("supplier-1", state.ServiceId);
        Assert.Equal(3, state.Operations.Count);
        Assert.Equal("supplier-api.yaml", Assert.Single(uploadedNames));
    }

    private static void ThenFailureIsTruthful(Exception? failure, MicrocksState state)
    {
        Assert.IsType<HttpRequestException>(failure);
        Assert.Equal("failed", state.Status);
        Assert.Null(state.Mode);
    }

    public ValueTask InitializeAsync() => ValueTask.CompletedTask;
    public async ValueTask DisposeAsync()
    {
        client?.Dispose();
        if (native is not null) await native.DisposeAsync();
    }
}

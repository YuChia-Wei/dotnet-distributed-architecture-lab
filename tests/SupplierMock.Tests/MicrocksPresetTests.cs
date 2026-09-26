using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.RegularExpressions;

public sealed class MicrocksPresetTests : IDisposable
{
    private readonly NativeMicrocksHandler native = new();
    private readonly HttpClient client;
    private readonly MicrocksPresetController controller;

    public MicrocksPresetTests()
    {
        client = new HttpClient(native) { BaseAddress = new Uri("http://microcks:8080/"), Timeout = TimeSpan.FromSeconds(35) };
        controller = new MicrocksPresetController(client, Path.Combine(AppContext.BaseDirectory, "microcks"));
    }

    [Fact]
    [Trait("Scenario", "M02-invalid-mode")]
    public async Task Given_invalid_mode_When_checked_Then_no_native_upload_occurs()
    {
        GivenUnconfiguredNativeService();
        var valid = MicrocksPresetController.IsValidMode("http://evil.test/");
        var failure = await Record.ExceptionAsync(() => controller.ChangeAsync("../proxy", TestContext.Current.CancellationToken));
        ThenInvalidModeIsRejectedWithoutUpload(valid, failure);
    }

    [Fact]
    [Trait("Scenario", "M02-unconfigured-custom")]
    public async Task Given_unconfigured_or_native_custom_service_When_state_is_read_Then_mode_is_not_claimed()
    {
        GivenUnconfiguredNativeService();
        var unconfigured = await WhenReadingStateAsync();
        ThenUnconfiguredHasNoMode(unconfigured);
        GivenExternallyEditedNativeService();
        var custom = await WhenReadingStateAsync();
        ThenCustomHasNoMode(custom);
    }

    [Fact]
    [Trait("Scenario", "M02-proxy-readback")]
    public async Task Given_native_service_When_proxy_preset_is_uploaded_Then_filename_and_all_dispatchers_are_verified()
    {
        GivenUnconfiguredNativeService();
        var selected = await WhenSelectingProxyAsync();
        ThenProxyReadbackMatchesNative(selected, 1);
        GivenExternallyEditedNativeService();
        var externalEdit = await WhenReadingStateAsync();
        ThenCustomHasNoMode(externalEdit);
    }

    [Fact]
    [Trait("Scenario", "M02-upstream-failure")]
    public async Task Given_failed_native_upload_When_selecting_proxy_Then_failed_state_allows_explicit_retry()
    {
        GivenRejectedNativeUpload();
        var failure = await Record.ExceptionAsync(WhenSelectingProxyAsync);
        var failedState = await WhenReadingStateAsync();
        ThenFailureIsTruthful(failure, failedState);
        GivenNativeUploadRecovered();
        var recovered = await WhenSelectingProxyAsync();
        ThenProxyReadbackMatchesNative(recovered, 2);
    }

    [Theory]
    [InlineData("malformed-service")]
    [InlineData("malformed-operation")]
    [Trait("Scenario", "M02-malformed-native")]
    public async Task Given_malformed_native_json_When_reading_or_switching_Then_no_mode_is_claimed_and_failure_is_bounded(string shape)
    {
        GivenMalformedNativeService(shape);
        var state = await WhenReadingStateAsync();
        var failure = await Record.ExceptionAsync(WhenSelectingProxyAsync);
        var afterFailure = await WhenReadingStateAsync();
        ThenMalformedNativeStateIsUnavailable(state, failure, afterFailure);
    }

    [Fact]
    [Trait("Scenario", "M02-stale-native-dispatcher")]
    public async Task Given_import_retains_hybrid_post_When_selecting_mock_Then_only_supplier_post_is_updated_and_read_back()
    {
        native.PreserveHybridPostOnMockUpload = true;
        var selected = await controller.ChangeAsync("mock", TestContext.Current.CancellationToken);
        Assert.Equal("ready", selected.Status);
        Assert.Equal("mock", selected.Mode);
        Assert.Equal("supplier-api.yaml", Assert.Single(native.UploadedNames));
        var update = Assert.Single(native.OperationUpdates);
        Assert.Equal("supplier-1", update.ServiceId);
        Assert.Equal("POST /supplier/orders", update.Name);
        Assert.Equal("JS", update.Dispatcher);
        Assert.Contains("__unmatched_supplier_order__", update.DispatcherRules);
        Assert.DoesNotContain("proxyUrl", update.DispatcherRules);
        var readback = await WhenReadingStateAsync();
        Assert.Equal("mock", readback.Mode);
    }

    [Fact]
    [Trait("Scenario", "M02-native-update-failure")]
    public async Task Given_native_operation_update_fails_When_selecting_mock_Then_mode_stays_unconfirmed()
    {
        native.PreserveHybridPostOnMockUpload = true;
        native.RejectOperationUpdate = true;
        var failure = await Record.ExceptionAsync(() => controller.ChangeAsync("mock", TestContext.Current.CancellationToken));
        Assert.IsType<HttpRequestException>(failure);
        var state = await WhenReadingStateAsync();
        Assert.Equal("failed", state.Status);
        Assert.Null(state.Mode);
        Assert.Equal("PROXY_FALLBACK", state.Operations.Single(operation => operation.Name == "POST /supplier/orders").Dispatcher);
    }

    [Fact]
    [Trait("Scenario", "M02-native-pagination")]
    public async Task Given_supplier_is_on_second_native_page_When_reading_state_Then_proxy_mode_is_found()
    {
        native.Mode = "proxy";
        native.SupplierOnSecondPage = true;
        var state = await WhenReadingStateAsync();
        Assert.Equal("ready", state.Status);
        Assert.Equal("proxy", state.Mode);
        Assert.Contains(1, native.RequestedPages);
    }

    private void GivenUnconfiguredNativeService() => native.Mode = "unconfigured";
    private void GivenExternallyEditedNativeService() => native.Mode = "custom";
    private void GivenRejectedNativeUpload() => native.RejectUpload = true;
    private void GivenNativeUploadRecovered() => native.RejectUpload = false;
    private void GivenMalformedNativeService(string shape)
    {
        native.Mode = shape;
        native.PreserveMalformedReadbackAfterUpload = true;
    }

    private Task<MicrocksState> WhenReadingStateAsync() => controller.GetStateAsync(TestContext.Current.CancellationToken);
    private Task<MicrocksState> WhenSelectingProxyAsync() => controller.ChangeAsync("proxy", TestContext.Current.CancellationToken);

    private void ThenInvalidModeIsRejectedWithoutUpload(bool valid, Exception? failure)
    {
        Assert.False(valid);
        Assert.IsType<ArgumentException>(failure);
        Assert.Equal(0, native.UploadCount);
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

    private void ThenProxyReadbackMatchesNative(MicrocksState state, int expectedUploads)
    {
        Assert.Equal("ready", state.Status);
        Assert.Equal("proxy", state.Mode);
        Assert.Equal("supplier-1", state.ServiceId);
        Assert.Equal(3, state.Operations.Count);
        Assert.Equal(expectedUploads, native.UploadCount);
        Assert.All(native.UploadedNames, name => Assert.Equal("supplier-api.yaml", name));
    }

    private static void ThenFailureIsTruthful(Exception? failure, MicrocksState state)
    {
        Assert.IsType<HttpRequestException>(failure);
        Assert.Equal("failed", state.Status);
        Assert.Null(state.Mode);
    }

    private static void ThenMalformedNativeStateIsUnavailable(MicrocksState before, Exception? failure, MicrocksState after)
    {
        Assert.Equal("unavailable", before.Status);
        Assert.Null(before.Mode);
        Assert.IsType<InvalidDataException>(failure);
        Assert.Equal("unavailable", after.Status);
        Assert.Null(after.Mode);
    }

    public void Dispose()
    {
        client.Dispose();
        native.Dispose();
    }

    private sealed class NativeMicrocksHandler : HttpMessageHandler
    {
        public string Mode { get; set; } = "unconfigured";
        public bool RejectUpload { get; set; }
        public bool PreserveMalformedReadbackAfterUpload { get; set; }
        public bool PreserveHybridPostOnMockUpload { get; set; }
        public bool RejectOperationUpdate { get; set; }
        public bool SupplierOnSecondPage { get; set; }
        public int UploadCount { get; private set; }
        public List<string> UploadedNames { get; } = [];
        public List<int> RequestedPages { get; } = [];
        public List<(string ServiceId, string Name, string Dispatcher, string DispatcherRules)> OperationUpdates { get; } = [];
        private string? mockPostRules;

        protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
        {
            var path = request.RequestUri?.AbsolutePath;
            if (request.Method == HttpMethod.Get && path == "/api/services")
            {
                var page = int.Parse(request.RequestUri!.Query.Split('&').Single(part => part.StartsWith("?page=", StringComparison.Ordinal))[6..]);
                RequestedPages.Add(page);
                object services = SupplierOnSecondPage && page == 0
                    ? Enumerable.Range(0, 100).Select(index => (object)new { id = $"other-{index}", name = $"Other {index}", version = "1.0.0" }).ToArray()
                    : SupplierOnSecondPage && page > 1 ? Array.Empty<object>() : NativeServices();
                return new HttpResponseMessage(HttpStatusCode.OK) { Content = JsonContent.Create(services) };
            }

            if (request.Method == HttpMethod.Post && path == "/api/artifact/upload")
            {
                UploadCount++;
                if (RejectUpload) return new HttpResponseMessage(HttpStatusCode.ServiceUnavailable);
                Assert.NotNull(request.Content);
                Assert.StartsWith("multipart/form-data", request.Content.Headers.ContentType?.MediaType);
                var body = await request.Content.ReadAsStringAsync(cancellationToken);
                var filename = Regex.Match(body, @"filename=""?(?<name>[^"";\r\n]+)");
                Assert.True(filename.Success);
                Assert.Contains("Supplier API", body);
                UploadedNames.Add(filename.Groups["name"].Value);
                if (!PreserveMalformedReadbackAfterUpload)
                    Mode = body.Contains("proxy each imported operation", StringComparison.Ordinal) ? "proxy"
                        : PreserveHybridPostOnMockUpload && body.Contains("External supplier sandbox contract", StringComparison.Ordinal) ? "stale-mock"
                        : "custom";
                return new HttpResponseMessage(HttpStatusCode.OK) { Content = JsonContent.Create(new { imported = true }) };
            }
            if (request.Method == HttpMethod.Put && path == "/api/services/supplier-1/operation")
            {
                if (RejectOperationUpdate) return new HttpResponseMessage(HttpStatusCode.ServiceUnavailable);
                using var document = JsonDocument.Parse(await request.Content!.ReadAsStreamAsync(cancellationToken));
                var operation = document.RootElement;
                var name = operation.GetProperty("name").GetString()!;
                var dispatcher = operation.GetProperty("dispatcher").GetString()!;
                var rules = operation.GetProperty("dispatcherRules").GetString()!;
                OperationUpdates.Add(("supplier-1", name, dispatcher, rules));
                if (Mode == "stale-mock" && name == "POST /supplier/orders")
                {
                    mockPostRules = rules;
                    Mode = "mock-updated";
                }
                return new HttpResponseMessage(HttpStatusCode.OK);
            }
            return new HttpResponseMessage(HttpStatusCode.NotFound);
        }

        private object NativeServices() => Mode switch
        {
            "unconfigured" => Array.Empty<object>(),
            "malformed-service" => new object?[] { null },
            "malformed-operation" => new[] { new { id = "supplier-1", name = "Supplier API", version = "1.0.0", operations = new object?[] { null } } },
            "proxy" => new[] { new { id = "supplier-1", name = "Supplier API", version = "1.0.0", operations = ProxyOperations() } },
            "stale-mock" => new[] { new { id = "supplier-1", name = "Supplier API", version = "1.0.0", operations = MockOperations("PROXY_FALLBACK", "{\"dispatcher\":\"JS\",\"proxyUrl\":\"http://supplier-sandbox:8080/\"}") } },
            "mock-updated" => new[] { new { id = "supplier-1", name = "Supplier API", version = "1.0.0", operations = MockOperations("JS", mockPostRules!) } },
            _ => new[] { new { id = "supplier-1", name = "Supplier API", version = "1.0.0", operations = new[]
            {
                new { name = "GET /supplier/catalog/{sku}", method = "GET", dispatcher = "PROXY", dispatcherRules = "http://changed-upstream:8080/" }
            } } }
        };

        private static object[] ProxyOperations() =>
        [
            new { name = "GET /supplier/catalog/{sku}", method = "GET", dispatcher = "PROXY", dispatcherRules = "http://supplier-sandbox:8080/" },
            new { name = "POST /supplier/orders", method = "POST", dispatcher = "PROXY", dispatcherRules = "http://supplier-sandbox:8080/" },
            new { name = "GET /supplier/orders/by-client-request/{clientRequestId}", method = "GET", dispatcher = "PROXY", dispatcherRules = "http://supplier-sandbox:8080/" }
        ];

        private static object[] MockOperations(string dispatcher, string rules) =>
        [
            new { name = "GET /supplier/catalog/{sku}", method = "GET", dispatcher = "URI_PARTS", dispatcherRules = "sku" },
            new { name = "POST /supplier/orders", method = "POST", dispatcher, dispatcherRules = rules },
            new { name = "GET /supplier/orders/by-client-request/{clientRequestId}", method = "GET", dispatcher = "URI_PARTS", dispatcherRules = "clientRequestId" }
        ];
    }
}

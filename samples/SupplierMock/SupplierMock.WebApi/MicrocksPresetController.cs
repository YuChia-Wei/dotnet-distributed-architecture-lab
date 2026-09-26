using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.RegularExpressions;

/// <summary>Microcks 原生服務回報的單一操作與派送設定。</summary>
/// <param name="Name">原生操作名稱。</param>
/// <param name="Method">HTTP 方法。</param>
/// <param name="Dispatcher">原生派送器名稱。</param>
/// <param name="DispatcherRules">原生派送規則。</param>
public sealed record MicrocksOperation(string Name, string Method, string? Dispatcher, string? DispatcherRules)
{
    /// <summary>保留原生操作的其他可變欄位，供派送設定更新時原樣帶回；不輸出至控制 API。</summary>
    [JsonIgnore]
    public JsonElement? NativeFields { get; init; }
}

/// <summary>供應商 Microcks 控制狀態；模式僅在原生操作完整符合已知預設時提供。</summary>
/// <param name="Mode">確認的預設模式；未知、失敗或讀取中斷時為 null。</param>
/// <param name="Status">目前控制狀態。</param>
/// <param name="ServiceId">Microcks 原生服務識別碼。</param>
/// <param name="ServiceName">固定服務名稱。</param>
/// <param name="ServiceVersion">固定服務版本。</param>
/// <param name="Operations">原生操作與派送設定。</param>
/// <param name="Message">供操作員參考的狀態說明。</param>
public sealed record MicrocksState(
    string? Mode,
    string Status,
    string? ServiceId,
    string ServiceName,
    string ServiceVersion,
    IReadOnlyList<MicrocksOperation> Operations,
    string? Message);

/// <summary>在固定 Microcks 來源套用三份隨程式封裝的供應商 API 預設。</summary>
/// <param name="client">只連至已設定 Microcks 來源的 HTTP 用戶端。</param>
/// <param name="presetDirectory">隨程式發佈的預設檔目錄。</param>
public sealed class MicrocksPresetController(HttpClient client, string presetDirectory)
{
    private const string ServiceName = "Supplier API";
    private const string ServiceVersion = "1.0.0";
    private const int ServicePageSize = 100;
    private const int MaxServicePages = 10;
    private static readonly string[] Modes = ["mock", "proxy", "hybrid"];
    private readonly SemaphoreSlim changeGate = new(1, 1);
    private volatile bool applying;
    private volatile bool failed;

    /// <summary>判斷名稱是否為三種明確允許的預設模式。</summary>
    /// <param name="mode">待檢查的模式。</param>
    /// <returns>模式是否有效。</returns>
    public static bool IsValidMode(string? mode) => mode is "mock" or "proxy" or "hybrid";

    /// <summary>驗證設定中的 Microcks 來源為固定允許的 HTTP 主機。</summary>
    /// <param name="value">設定的來源網址。</param>
    /// <returns>已驗證的絕對來源網址。</returns>
    public static Uri ValidateMicrocksOrigin(string value)
    {
        if (!Uri.TryCreate(value, UriKind.Absolute, out var uri)
            || uri.Scheme != Uri.UriSchemeHttp
            || !string.IsNullOrEmpty(uri.UserInfo)
            || uri.Query.Length != 0
            || uri.Fragment.Length != 0
            || uri.AbsolutePath != "/"
            || uri.Host is not ("microcks" or "localhost" or "127.0.0.1" or "::1"))
        {
            throw new InvalidOperationException("SupplierMock:MicrocksUrl must be a fixed Microcks HTTP origin.");
        }

        return uri;
    }

    /// <summary>讀取原生服務並依完整操作派送設定判定目前模式。</summary>
    /// <param name="cancellationToken">讀取取消權杖。</param>
    /// <returns>即時 Microcks 控制狀態。</returns>
    public async Task<MicrocksState> GetStateAsync(CancellationToken cancellationToken = default)
    {
        if (applying)
        {
            return NewState(null, "applying", null, [], "正在套用 Microcks 預設。完成後請重新讀取狀態。");
        }

        try
        {
            using var timeout = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
            timeout.CancelAfter(TimeSpan.FromSeconds(10));
            var native = await ReadNativeAsync(timeout.Token);
            if (native is null)
            {
                return NewState(null, failed ? "failed" : "unconfigured", null, [],
                    failed ? "上次匯入失敗；Microcks 尚無 Supplier API。" : null);
            }

            var matched = Modes.FirstOrDefault(mode => SameOperations(native.Value.Operations, LoadExpected(mode)));
            var status = failed ? "failed" : matched is null ? "custom" : "ready";
            return NewState(failed ? null : matched, status, native.Value.Id, native.Value.Operations,
                failed ? "上次匯入未能驗證；請檢查原生設定後明確重試。" : matched is null ? "原生設定與已知預設不一致。" : null);
        }
        catch (Exception ex) when (ex is HttpRequestException or OperationCanceledException or JsonException or InvalidDataException)
        {
            return NewState(null, "unavailable", null, [], "無法讀取 Microcks 原生服務狀態。");
        }
    }

    /// <summary>序列化套用固定預設；取得閘門後即使呼叫端斷線也會在時限內完成或失敗。</summary>
    /// <param name="mode">三種固定預設之一。</param>
    /// <param name="requestCancellation">等待套用閘門時的呼叫端取消權杖。</param>
    /// <returns>匯入後由原生操作確認的狀態。</returns>
    public async Task<MicrocksState> ChangeAsync(string mode, CancellationToken requestCancellation = default)
    {
        if (!IsValidMode(mode)) throw new ArgumentException("Invalid Microcks mode.", nameof(mode));
        await changeGate.WaitAsync(requestCancellation);
        try
        {
            applying = true;
            failed = false;
            using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(35));
            var artifact = await File.ReadAllBytesAsync(Path.Combine(presetDirectory, $"supplier-{mode}.yaml"), timeout.Token);
            using var form = new MultipartFormDataContent();
            using var file = new ByteArrayContent(artifact);
            file.Headers.ContentType = new MediaTypeHeaderValue("application/yaml");
            form.Add(file, "file", "supplier-api.yaml");
            using var response = await client.PostAsync("api/artifact/upload?mainArtifact=true", form, timeout.Token);
            response.EnsureSuccessStatusCode();

            // Import processing may finish after upload returns. Verify the native dispatcher set, not only identity.
            var expected = LoadExpected(mode);
            var deadline = DateTime.UtcNow.AddSeconds(20);
            var reconciled = false;
            do
            {
                var native = await ReadNativeAsync(timeout.Token);
                if (native is not null && SameOperations(native.Value.Operations, expected))
                {
                    applying = false;
                    return NewState(mode, "ready", native.Value.Id, native.Value.Operations, null);
                }
                if (native is not null && !reconciled && SameOperationIdentities(native.Value.Operations, expected))
                {
                    // A native operation edit can survive a main-artifact import. Reconcile only
                    // this fixed service's three known operations, then verify the native state again.
                    foreach (var wanted in expected)
                    {
                        var actual = native.Value.Operations.Single(operation => operation.Name == wanted.Name && operation.Method == wanted.Method);
                        if (actual.Dispatcher == wanted.Dispatcher && SameRules(actual.DispatcherRules, wanted.DispatcherRules)) continue;
                        using var update = await client.PutAsJsonAsync(
                            $"api/services/{Uri.EscapeDataString(native.Value.Id)}/operation?operationName={Uri.EscapeDataString(actual.Name)}",
                            new
                            {
                                wanted.Dispatcher,
                                wanted.DispatcherRules,
                                DefaultDelay = NativeField(actual.NativeFields, "defaultDelay"),
                                DefaultDelayStrategy = NativeField(actual.NativeFields, "defaultDelayStrategy"),
                                ParameterConstraints = NativeField(actual.NativeFields, "parameterConstraints")
                            }, timeout.Token);
                        update.EnsureSuccessStatusCode();
                    }
                    reconciled = true;
                }
                await Task.Delay(250, timeout.Token);
            } while (DateTime.UtcNow < deadline);

            throw new InvalidDataException("Microcks upload did not produce the expected dispatcher set.");
        }
        catch
        {
            failed = true;
            throw;
        }
        finally
        {
            applying = false;
            changeGate.Release();
        }
    }

    private async Task<(string Id, IReadOnlyList<MicrocksOperation> Operations)?> ReadNativeAsync(CancellationToken cancellationToken)
    {
        (string Id, IReadOnlyList<MicrocksOperation> Operations)? selected = null;
        for (var page = 0; page < MaxServicePages; page++)
        {
            using var response = await client.GetAsync($"api/services?page={page}&size={ServicePageSize}", cancellationToken);
            response.EnsureSuccessStatusCode();
            using var document = JsonDocument.Parse(await response.Content.ReadAsStreamAsync(cancellationToken));
            if (document.RootElement.ValueKind != JsonValueKind.Array) throw new InvalidDataException("Microcks service list is not an array.");
            foreach (var service in document.RootElement.EnumerateArray())
            {
                if (service.ValueKind != JsonValueKind.Object) throw new InvalidDataException("Microcks service entry is not an object.");
                if (RequiredString(service, "name") != ServiceName || RequiredString(service, "version") != ServiceVersion) continue;
                if (selected is not null) throw new InvalidDataException("Microcks has duplicate Supplier API versions.");
                var id = RequiredString(service, "id");
                if (string.IsNullOrWhiteSpace(id)) throw new InvalidDataException("Microcks service id is missing.");
                if (!service.TryGetProperty("operations", out var operations) || operations.ValueKind != JsonValueKind.Array)
                    throw new InvalidDataException("Microcks service operations are missing.");
                var parsed = new List<MicrocksOperation>();
                foreach (var operation in operations.EnumerateArray())
                {
                    if (operation.ValueKind != JsonValueKind.Object) throw new InvalidDataException("Microcks operation entry is not an object.");
                    parsed.Add(new MicrocksOperation(
                        RequiredString(operation, "name"),
                        RequiredString(operation, "method"),
                        ReadOptional(operation, "dispatcher"),
                        ReadOptional(operation, "dispatcherRules")) { NativeFields = operation.Clone() });
                }
                selected = (id, parsed);
            }
            if (document.RootElement.GetArrayLength() < ServicePageSize) return selected;
        }
        throw new InvalidDataException("Microcks service listing exceeded the bounded page limit.");
    }

    private static string RequiredString(JsonElement element, string property) =>
        element.ValueKind == JsonValueKind.Object && element.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.String
            ? value.GetString() ?? ""
            : throw new InvalidDataException($"Microcks service field {property} is missing.");

    private static string? ReadOptional(JsonElement element, string property) =>
        element.ValueKind == JsonValueKind.Object && element.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.String ? value.GetString() : null;

    private static JsonElement? NativeField(JsonElement? operation, string property) =>
        operation is { ValueKind: JsonValueKind.Object } native && native.TryGetProperty(property, out var value)
            ? value.Clone() : null;

    private static MicrocksState NewState(string? mode, string status, string? id,
        IReadOnlyList<MicrocksOperation> operations, string? message) =>
        new(mode, status, id, ServiceName, ServiceVersion, operations, message);

    private static bool SameOperations(IReadOnlyList<MicrocksOperation> actual, IReadOnlyList<MicrocksOperation> expected) =>
        actual.Count == expected.Count && expected.All(wanted => actual.Count(candidate =>
            candidate.Name == wanted.Name && candidate.Method == wanted.Method
            && candidate.Dispatcher == wanted.Dispatcher
            && SameRules(candidate.DispatcherRules, wanted.DispatcherRules)) == 1);

    private static bool SameOperationIdentities(IReadOnlyList<MicrocksOperation> actual, IReadOnlyList<MicrocksOperation> expected) =>
        actual.Count == expected.Count && expected.All(wanted => actual.Count(candidate =>
            candidate.Name == wanted.Name && candidate.Method == wanted.Method) == 1);

    private static bool SameRules(string? actual, string? expected)
    {
        if (actual == expected) return true;
        if (actual is null || expected is null) return false;
        try
        {
            using var left = JsonDocument.Parse(actual);
            using var right = JsonDocument.Parse(expected);
            return JsonElement.DeepEquals(left.RootElement, right.RootElement);
        }
        catch (JsonException)
        {
            return actual.Replace("\r\n", "\n", StringComparison.Ordinal).TrimEnd() ==
                expected.Replace("\r\n", "\n", StringComparison.Ordinal).TrimEnd();
        }
    }

    // The bundled artifacts have a deliberately bounded shape. Parse only their operation extensions;
    // do not accept user-supplied YAML or treat this as a general YAML parser.
    private IReadOnlyList<MicrocksOperation> LoadExpected(string mode)
    {
        var lines = File.ReadAllLines(Path.Combine(presetDirectory, $"supplier-{mode}.yaml"));
        var result = new List<MicrocksOperation>();
        string? path = null;
        string? method = null;
        for (var i = 0; i < lines.Length; i++)
        {
            var line = lines[i];
            if (Regex.IsMatch(line, @"^  /[^:]+:$")) { path = line.Trim().TrimEnd(':'); continue; }
            if (Regex.IsMatch(line, @"^    (get|post|put|delete):$"))
            {
                method = line.Trim().TrimEnd(':').ToUpperInvariant();
                if (path is null) throw new InvalidDataException("Microcks artifact has an operation without path.");
                var variable = Regex.Match(path, @"\{([^}]+)\}");
                result.Add(new MicrocksOperation($"{method} {path}", method,
                    variable.Success ? "URI_PARTS" : null, variable.Success ? variable.Groups[1].Value : null));
                continue;
            }
            if (!line.StartsWith("      x-microcks-operation:", StringComparison.Ordinal) || result.Count == 0) continue;
            var dispatcher = "";
            var rules = "";
            if (line.Contains('{', StringComparison.Ordinal))
            {
                var match = Regex.Match(line, @"dispatcher: ([A-Z_]+), dispatcherRules: '([^']*)'");
                if (!match.Success) throw new InvalidDataException("Unsupported inline Microcks extension.");
                dispatcher = match.Groups[1].Value;
                rules = match.Groups[2].Value;
            }
            else
            {
                dispatcher = lines[++i].Trim()["dispatcher: ".Length..];
                var rulesLine = lines[++i].Trim();
                if (!rulesLine.StartsWith("dispatcherRules: ", StringComparison.Ordinal)) throw new InvalidDataException("Missing dispatcher rules.");
                var value = rulesLine["dispatcherRules: ".Length..];
                if (value == "|")
                {
                    var block = new List<string>();
                    while (i + 1 < lines.Length && lines[i + 1].StartsWith("          ", StringComparison.Ordinal))
                        block.Add(lines[++i][10..]);
                    rules = string.Join('\n', block) + "\n";
                }
                else rules = value.Trim('\'');
            }
            result[^1] = result[^1] with { Dispatcher = dispatcher, DispatcherRules = rules };
        }
        if (result.Count != 3) throw new InvalidDataException("Microcks preset must contain three operations.");
        return result;
    }
}

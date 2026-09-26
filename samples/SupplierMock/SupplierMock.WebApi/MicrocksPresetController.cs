using System.Net;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;

public sealed record MicrocksOperation(string Name, string Method, string? Dispatcher, string? DispatcherRules);

public sealed record MicrocksState(
    string? Mode,
    string Status,
    string? ServiceId,
    string ServiceName,
    string ServiceVersion,
    IReadOnlyList<MicrocksOperation> Operations,
    string? Message);

/// <summary>Controls only the three repository-owned Supplier API artifacts on one configured Microcks origin.</summary>
public sealed class MicrocksPresetController(HttpClient client, string presetDirectory)
{
    private const string ServiceName = "Supplier API";
    private const string ServiceVersion = "1.0.0";
    private static readonly string[] Modes = ["mock", "proxy", "hybrid"];
    private readonly SemaphoreSlim changeGate = new(1, 1);
    private volatile bool applying;
    private volatile bool failed;

    public static bool IsValidMode(string? mode) => mode is "mock" or "proxy" or "hybrid";

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

    /// <summary>The request may disconnect after the gate is acquired; the bounded import still completes.</summary>
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
            do
            {
                var native = await ReadNativeAsync(timeout.Token);
                if (native is not null && SameOperations(native.Value.Operations, expected))
                {
                    applying = false;
                    return NewState(mode, "ready", native.Value.Id, native.Value.Operations, null);
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
        using var response = await client.GetAsync("api/services?page=0&size=100", cancellationToken);
        response.EnsureSuccessStatusCode();
        using var document = JsonDocument.Parse(await response.Content.ReadAsStreamAsync(cancellationToken));
        if (document.RootElement.ValueKind != JsonValueKind.Array) throw new InvalidDataException("Microcks service list is not an array.");
        (string Id, IReadOnlyList<MicrocksOperation> Operations)? selected = null;
        foreach (var service in document.RootElement.EnumerateArray())
        {
            if (RequiredString(service, "name") != ServiceName || RequiredString(service, "version") != ServiceVersion) continue;
            if (selected is not null) throw new InvalidDataException("Microcks has duplicate Supplier API versions.");
            var id = RequiredString(service, "id");
            if (string.IsNullOrWhiteSpace(id)) throw new InvalidDataException("Microcks service id is missing.");
            if (!service.TryGetProperty("operations", out var operations) || operations.ValueKind != JsonValueKind.Array)
                throw new InvalidDataException("Microcks service operations are missing.");
            selected = (id, operations.EnumerateArray().Select(operation => new MicrocksOperation(
                RequiredString(operation, "name"),
                RequiredString(operation, "method"),
                ReadOptional(operation, "dispatcher"),
                ReadOptional(operation, "dispatcherRules"))).ToArray());
        }
        return selected;
    }

    private static string RequiredString(JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.String
            ? value.GetString() ?? ""
            : throw new InvalidDataException($"Microcks service field {property} is missing.");

    private static string? ReadOptional(JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.String ? value.GetString() : null;

    private static MicrocksState NewState(string? mode, string status, string? id,
        IReadOnlyList<MicrocksOperation> operations, string? message) =>
        new(mode, status, id, ServiceName, ServiceVersion, operations, message);

    private static bool SameOperations(IReadOnlyList<MicrocksOperation> actual, IReadOnlyList<MicrocksOperation> expected) =>
        actual.Count == expected.Count && expected.All(wanted => actual.Count(candidate =>
            candidate.Name == wanted.Name && candidate.Method == wanted.Method
            && candidate.Dispatcher == wanted.Dispatcher
            && SameRules(candidate.DispatcherRules, wanted.DispatcherRules)) == 1);

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

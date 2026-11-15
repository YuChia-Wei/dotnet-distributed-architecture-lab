# .NET snippet tool

Source builds use the Framework checkout's
`src/tools/dotnet/generation/snippet-tool` directory, which contains
`SnippetTool.csproj`. Run the build/publish commands below from that directory.
This manual is also included in the standalone artifact; running that artifact
requires neither the source checkout nor a knowledge-package installation.

SnippetTool renders small C# fragments for a human or agent to insert into a selected context. The release bundle contains a Native AOT executable for each supported platform, this README, and the shipped `snippets/` catalog and body files beside each executable. Install the .NET 10 SDK for development and generated-code compilation. The native executable includes its required runtime support and can run from any working directory. The explicit framework-dependent comparison variant uses the host runtime; configure apphost lookup (for example, `DOTNET_ROOT_X64`) for custom .NET installations. Missing-runtime diagnostics for that variant occur before the application JSON contract starts. The snippet output is ordinary C# and the consuming project only needs the types and APIs listed by the selected snippet.

## Run

On Windows use `SnippetTool.exe`. On Unix use `./SnippetTool`. The executable also accepts `--help` and `--version`. For a request, pass `--request request.json`. For example, save this request to inspect the interface snippet:

```json
{"schemaVersion":1,"operation":"inspect","id":"interface-method"}
```

Render the same snippet with a method name and an explicit return type:

```json
{"schemaVersion":1,"operation":"render","id":"interface-method","parameters":{"methodName":"ReadAsync","returnType":"Task<string>"},"indent":4}
```

Use the returned `text` as the fragment and the returned `snippet` metadata for insertion context, required using directives and preconditions. Include the relevant using directives in the surrounding C# before compiling it.

| Operation | Additional request fields | Response fields |
| --- | --- | --- |
| `list` | None | `snippets` contains metadata summaries sorted by ID |
| `search` | `query`, a nonblank string | `snippets` contains matching summaries sorted by ID |
| `inspect` | `id` | `snippet` contains metadata and parameter declarations, and `body` contains the raw template |
| `render` | `id`, optional `parameters`, optional `indent` and `newline` | `snippet` contains metadata and `text` contains the expanded fragment |

Each request takes optional `source`, a path to the selected catalog JSON. A relative source path resolves against the directory of the request file. An omitted or null source selects `snippets/catalog.json` next to the executable. A selected source is authoritative for that invocation and unreadable or invalid selections fail. List and search read catalog metadata only. Search matches case-insensitive substrings in IDs, titles, descriptions, contexts and tags. Inspect and render read and validate the selected body's placeholder syntax.

Requests, catalogs and bodies are UTF-8 with an optional BOM. The request and catalog schema versions are both `1`. Request property names and all IDs and parameter names are case-sensitive. Optional request fields with JSON null are treated as omitted. JSON objects reject unrecognized fields and duplicate properties. Success returns exit code 0 and one UTF-8 JSON line on stdout with `schemaVersion`, `operation`, `source` and the operation-specific fields. Failure returns exit code 1 and a JSON line on stderr with `schemaVersion` and `error` containing a stable `code` and explanatory `message`. For example, a render can fail with `missing-parameter`, `unknown-parameter` or `invalid-parameter`. Keep the executable and assets in a trusted tool directory. The tool reads the selected files and writes its result to the console.

## Catalog and rendering rules

Requests, catalogs and bodies must be nonempty files. Zero-length inputs are
rejected before opening them, including Unix FIFOs reporting zero length.
Keep selected files stable during an invocation; this is not a filesystem sandbox.

Use the shipped catalog as a worked example for a custom catalog. A catalog has a `schemaVersion`, a `source` object with `id` and `version`, and a `snippets` array. Source and snippet IDs use lower-case ASCII letters, digits and hyphen-separated segments, starting with a letter. Source versions have numeric major, minor and patch components and an optional prerelease suffix such as `1.2.0-preview.1`. They identify the source content independently of the executable version. Increment your source version when distributing changed catalog or body content.

Each snippet declares `id`, `title`, `description`, `context`, `bodyFile`, `tags`, `requiredUsings`, `preconditions` and `parameters`. The `tags`, `requiredUsings` and `preconditions` fields use arrays of strings. `parameters` is an object keyed by parameter name. Keep body files next to the selected catalog with names such as `my-method.snippet`. Body file stems follow snippet ID syntax. Symlink or reparse-point body files are rejected. Edit a separate catalog copy to customize the shipped content, and choose it with `source`.

A parameter declaration has `kind` and an optional string `default`. Without a default it requires a supplied string. A default of `""` is available for `text`. `enum` also requires an array of distinct nonblank string `values` and compares values case-sensitively. `identifier` accepts ASCII letters and underscores followed by ASCII letters, digits or underscores, excluding C# reserved keywords. Check contextual restrictions at the insertion site. `text` substitutes a string as supplied, so choose a body and text values that are safe for the intended C# context. The tool evaluates no expressions and performs no C# escaping or semantic checking. The built-in interface snippet uses explicit enum choices for types.

Use `${name}` to reference a declared parameter and `$${` to output a literal `${` opener. The renderer scans the body once. It copies ordinary text, including C# braces and quotes, and leaves token-like text inside parameter values untouched. It replaces repeated references with the same value. A malformed or undeclared placeholder fails. It normalizes CRLF, CR and LF across the expanded text to the requested `newline` (`lf` by default or `crlf`). It prefixes every nonempty line with `indent` spaces (0 by default, 0–256 allowed), preserves blank lines, and preserves whether the expanded text ends in a newline.

## Build a platform package

Select the runtime identifier, preview or release version and a fresh output directory. For example:

```powershell
dotnet publish ./SnippetTool.csproj -c Release -r win-x64 --self-contained false -p:PublishSingleFile=true -p:DebugType=None -p:Version=0.1.0-dev.1 -o <publish-directory>
```

Archive the publish directory with the platform and version in its filename. Keep the catalog and body files in `snippets/` beside the executable. Use `Publish-Snippets.ps1` from the generation source directory for standalone framework-dependent single-file delivery with debug symbols omitted. For the optional Native AOT variant, add `-NativeAot` to that script. It publishes a self-contained native executable with the required runtime support, requires the platform-native compiler toolchain at build time, and uses the same compilation mode as the release bundle, with a separate standalone archive. AOT compatibility analysis remains enabled in the project. Selecting this variant does not change the host-SDK development prerequisites or require SDK-free environment acceptance. Compare startup, memory and size using the same source and inputs before choosing a delivery mode. The executable's project version is a local preview.

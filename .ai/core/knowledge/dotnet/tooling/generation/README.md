# .NET generation

For development from a specification or accepted interface, start with the
[development workflow](../development-tools.md). The generation bundle is
optional; use it when a supplied template or fragment fits the selected operation.

To use the release's `generation` bundle, install it with `install-generation.py --project
<project-root>`. It places tools in `.ai/tools/dotnet-generation`. See the
[delivery guide](DELIVERY.md) for directory/package registration, platform
executables, installation diagnostics and tool version/control guidance.

## Choose a generator

| Template | Output | Target |
| --- | --- | --- |
| `aicf-miniapi` | One project with Domain/Application/Infrastructure folders | .NET 10 Minimal API, `/work-items` |
| `aicf-webapi` | Domain, Application, Infrastructure and WebApi projects in a `.slnx` | .NET 10 controller API, `/api/work-items` |
| `aicf-usecase` | Interface, implementation, input and output | C# application item |
| `aicf-class` | One class | C# item |
| `aicf-interface` | One interface | C# item |
| `aicf-domain-contract-tests` | xUnit reconstruction example with its own illustrative domain code | .NET 10 |
| `aicf-ct005-contract-tests` | xUnit example against the published ArchPrecept CT-005 API | .NET 8 with verified external DLLs |

`aicf-usecase` emits a fixed interface/implementation/input/output structure.
It does not read an arbitrary existing interface or derive business behavior
from a specification. Use only the structure accepted by the target; when an
interface already exists, implement its actual contract through a suitable IDE
operation or AI editing, then validate it. Do not create a second interface or
force this template onto a different architecture.

API starters store work items in memory. POST `{"title":"Pack the order"}` to
the route, then GET the response's `Location`. Replace this sample behavior with
the accepted domain behavior. Generated applications have no tool dependency.

`--name` replaces the starter's project names and root namespace; `WorkItem`
and its routes remain a fixed reference feature. The controller starter uses
`<name>.Controllers` and `<name>.Models.*` inside the `<name>.WebApi` project;
the project suffix is not part of those namespaces. Adapt the sample to the
target's naming rules. Both starters use the host's default error behavior:
Minimal API responses can be empty, while `[ApiController]` supplies
ProblemDetails and content-type checks. For example, a POST without body or
Content-Type yields 400 in the Minimal API and 415 in the controller starter.
They do not define a shared production error contract; select one when replacing
the reference feature.

The API starters and package-free domain contract example target `net10.0`.
Item templates emit C# without selecting a project TFM. The optional CT-005
example targets `net8.0` and requires both published ArchPrecept contract DLLs
at version `0.0.3-preview` through `PublishedContractsDir`.

Register either an extracted template directory or the packaged `.nupkg` as
shown in the delivery guide, then use `dotnet new <short-name> --help`.
For items, choose a valid type name and `--namespace`; preview paths with
`--dry-run` and resolve collisions before writing. The namespace defaults to
`Example`; supply the target namespace explicitly. Run a generated WebApi via
`dotnet run --project <output>/WebApi/<name>.WebApi.csproj`.

Choose a template after the target accepts the host or operation boundary and
its dependencies. Use the [Web API setup](../../application-types/web-api/setup.md),
[Use Case contract](../../architecture/ddd-cqrs/usecase-standards.md) or [domain
contract examples](../../testing/domain-contract-examples.md) where applicable.
Generated files belong to the target. Inspect and adapt them, then compile and
verify the affected behavior with the target's selected checks.

## Insert a fragment

[SnippetTool](snippet-tool/README.md) supports `list`, `search`, `inspect` and
`render`. Inspect the context, parameters and usings before rendering. It returns
text; the caller inserts it and validates the affected code.

Available fragments: interface method, string/null/cancellation guards,
constructor assignment, Guid ID, readonly property, domain interfaces and
optional ES aggregate mechanics. ES is selected only by the target's architecture.

Keep custom catalogs outside managed tools and select them with `source`.
For custom native templates, extract the nupkg into a target-owned directory,
change identity/name/shortName, then register that directory. Template sources
and `.template.config` are delivered inside the nupkg and can be extracted as a
complete directory for direct registration without building a new package.

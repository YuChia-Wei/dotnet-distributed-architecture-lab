# .NET generation and formatting tools

Install this complete directory into an existing project:

```text
python install-generation.py --project /path/to/project
```

The installer verifies the manifest and writes `.ai/tools/dotnet-generation`.
Current bundles include `formatting/Format-Dotnet.ps1` and its manual. The script
uses PowerShell 7.3+ and invokes the workspace-selected SDK through `dotnet` on
PATH. See `formatting/README.md` for selected-file checks, explicit apply and
direct SDK usage from other shells. An unchanged installation of a prior bundle
can be replaced with the same installer. Update formatter callers to use SDK
arguments and output in place of the former FormatTool JSON API.

The release bundle publishes SnippetTool with Native AOT on its Windows x64 and
Linux x64 runners. Each executable contains its runtime support. The
`native-aot` mode in `generation.json` identifies the snippet delivery.
Maintainers can select a framework-dependent CoreCLR comparison build, and
older CoreCLR manifests remain supported. SnippetTool's standalone
`Publish-Snippets.ps1` retains its host-SDK default and selects AOT with
`-NativeAot`. Snippet catalogs and templates remain external data.
The installer manages bundle files. SDK installation, template registration and
source changes remain explicit development steps.

For the framework-dependent comparison variant, the .NET host reports missing
runtime failures before SnippetTool starts.

| Tool | Success / changes required | Failure |
| --- | --- | --- |
| `Format-Dotnet.ps1` | Native SDK output and exit code | Native SDK output and exit code, or PowerShell errors for invalid script inputs |
| `SnippetTool --request` | stdout JSON, exit 0 | stderr JSON, exit 1 |
| `install-generation.py` | stdout JSON, exit 0 | stderr JSON, exit 1 |

The formatter's default check can exit nonzero for required changes or an SDK
failure. Read the console diagnostics and any requested SDK report.

Updates replace only an unchanged previous installation; modified or unknown
files cause a refusal. Keep custom snippets and templates outside this directory.
This also applies to incidental files such as `.DS_Store`, `desktop.ini` and
`Thumbs.db`. Refusal reasons identify unknown paths (up to five file names per
list) or a missing manifest-listed member. Inspect the named paths and preserve
anything you own before reconciling them; the installer does not delete them
automatically. A missing member retains the `filesystem-error` code, while
unknown files or directories use `invalid-bundle`.

Use an existing project's physical path. The installer rejects symlinks and
Windows reparse points in the source, destination or their ancestors. Inspect
the link and explicitly supply the intended physical path (for example,
`realpath /path/to/project` on POSIX); it will not follow links automatically.

Success writes one JSON object to stdout and exits 0. Expected refusals and
filesystem errors write one JSON object to stderr and exit 1:
`{"outcome":"blocked","code":"bundle-changed","reason":"Changed bundle member: README.md"}`.
Use `code` for automation and `reason` for details. Codes are `invalid-arguments`,
`linked-path`, `project-not-found`, `invalid-bundle`, `bundle-changed`,
`overlapping-paths`, `pending-installation`, `concurrent-change`,
`invalid-recovery`, `recovery-conflict`, `filesystem-error` and `invalid-data`.
`--help` is human-readable. A nonzero result does not mean an interrupted
installation was rolled back; retain pending state and use recovery below.

After an interrupted installation, stop other installers, run
`python install-generation.py --project /path/to/project --recover`, then retry.
Recovery restores the verified previous installation or retains the completed
new one. If verification refuses recovery, preserve the reported staging and
target directories for manual reconciliation. The persistent `.lock` file is
normal; the operating system releases its lock when the process exits.

With the .NET 10 SDK, choose either registration path. Both use the same sources;
directory registration requires no package build or nupkg installation.

For a directory you own, extract the shipped nupkg as a ZIP into
`team-templates`, then register its `content` directory:

```text
dotnet new install ./team-templates/content
dotnet new list aicf
dotnet new aicf-webapi --name Orders --output Orders
dotnet new uninstall ./team-templates/content
```

Alternatively, register the installed package directly:

```text
dotnet new install .ai/tools/dotnet-generation/templates/AICF.Dotnet.Templates.<version>.nupkg
dotnet new list aicf
dotnet new aicf-webapi --name Orders --output Orders
```

The package includes `aicf-miniapi`, `aicf-webapi`, `aicf-usecase`, `aicf-class`,
`aicf-interface`, `aicf-domain-contract-tests` and `aicf-ct005-contract-tests`.
Use `--help` and `--dry-run` before generating into an existing project.
`dotnet new uninstall AICF.Dotnet.Templates` unregisters it.
For customization, change identity, name and shortName in each selected
`.template.config/template.json` before registering your directory. For example,
change `AiCollaboration.DotNet.AicfClass.1` to `MyTeam.DotNet.Class.1`,
`AI Collaboration C# Class` to `My Team C# Class`, and `aicf-class` to `myteam-class`.
The `.1` is part of the template identity, not the Framework package version.
Registering the same identity from multiple locations can shadow an earlier
registration. Keep your customized sources and generated code under your own
version control; compare upstream updates before adopting them.
The C# sources and `.template.config` inside the package are required by
`dotnet new`; they are not loose installed project files.

The two API starters and `aicf-domain-contract-tests` target `net10.0`. The
three item templates emit C# files without a project or TFM. Select the
destination namespace explicitly (`--namespace`, default `Example`) and compile
in the target project. In the API starters, `--name` changes project names and
namespaces. Replace the fixed `WorkItem` sample feature as a whole.

The package-free contract example includes its own illustrative domain code.
The optional `aicf-ct005-contract-tests` example needs the .NET 8 runtime
and the verified ArchPrecept.Contracts.Domain and
ArchPrecept.Contracts.Domain.EventSourcing `0.0.3-preview` assemblies. Use the
[ArchPrecept release record](https://github.com/YuChia-Wei/ArchPrecept/blob/main/docs/releases/0.0.3-preview.md)
to verify the packages, extract them under `domain/` and `eventsourcing/`
respectively, then pass their parent directory as `PublishedContractsDir`:

```text
dotnet new aicf-ct005-contract-tests --name Example.Ct005 --output Example.Ct005
dotnet test Example.Ct005/Example.Ct005.csproj -p:PublishedContractsDir=<verified-extracted-directory>
```

Run `snippets/win-x64/SnippetTool.exe` on Windows x64 or
`snippets/linux-x64/SnippetTool` on Linux x64 with `--request request.json`.
Each executable includes its .NET runtime. Keep the shipped `snippets/` directory
beside the executable. Linux needs the platform's native runtime dependencies
(Ubuntu 24.04 is the tested baseline).
macOS is not in the SnippetTool runtime matrix; separate trial binaries do not
establish supported installation or download trust. macOS delivery remains
future work tracked by Feature #582.
Use `{"schemaVersion":1,"operation":"list"}`, then inspect one ID before rendering it.
See `snippets/README.md` for request fields and customization.
Rendering returns text; insertion and compilation remain explicit steps.

`generation.json` identifies the source commit, release version and file hashes.
The application generated from a template does not depend on these tools.
Local preview labels such as `0.0.0-rc.N` identify snapshots; they do not allocate
the next release or sort above an existing formal version. When replacing a
preview, explicitly select the verified formal release and follow its normal
Framework update and separate generation-tool installation steps.

Treat `.ai/tools/dotnet-generation` as a reproducible local tool installation.
It includes both supported snippet runtimes. We recommend ignoring
the following paths in Git, while committing your custom sources and a setup
note identifying the trusted release and checksum to restore:

```gitignore
/.ai/tools/dotnet-generation/
/.ai/tools/.dotnet-generation-*
```

The installer does not edit `.gitignore`. On a new clone, obtain that release
and explicitly run its installer before selecting a generator. A missing
`generation.json` means no identifiable installed bundle; a different
`version`/`source_commit` from the selected release means a version mismatch.
Compare both fields with the release bundle before use or an explicit update.
Framework knowledge installation and `framework.lock`/`inspect` do not track
this separate tool installation or detect its version mismatch automatically.
Do not delete the other platform's files to reduce size: verification expects
the complete manifest. Unregister any native templates before removing an
unchanged tool installation; preserve custom directories and interrupted state.

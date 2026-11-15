# Domain contract test templates

Generate an illustrative xUnit project to explore the
[reconstruction cases](reconstruction-and-projector-cases.md). The examples help
targets design their own tests and choose their domain contracts and APIs.

## Package-free domain example

The six cases cover replay without pending events, confirmation of new facts,
reconstruction of a Plan with nested state, and rejection of absent, incomplete
or unsupported histories. The generated project includes self-contained
illustrative domain code and uses xUnit and BDDfy. Discard a partially restored
instance after replay fails. The optional CT-005 example verifies the published
API's stronger replay guards.

Use the .NET 10 SDK and the unified template package in the installed
generation bundle. Follow the [generation delivery guide](../tooling/generation/DELIVERY.md)
to locate the package. From a framework source checkout you can also select
`src/tools/dotnet/generation/dotnet-new` as the template source.
Generate into a disposable directory with an isolated native template hive.

```powershell
$templateSource = (Resolve-Path '<path-to-AICF.Dotnet.Templates.nupkg>').Path
$work = New-Item -ItemType Directory -Path (
    Join-Path ([IO.Path]::GetTempPath()) "aicf-domain-contracts-$([Guid]::NewGuid().ToString('N'))")
$hive = Join-Path $work.FullName 'hive'
$output = Join-Path $work.FullName 'package-free'

dotnet new install $templateSource --debug:custom-hive $hive
dotnet new aicf-domain-contract-tests --name Sample.DomainContracts --output $output --debug:custom-hive $hive
dotnet test (Join-Path $output 'Sample.DomainContracts.csproj') -c Release
```

## Optional published ArchPrecept CT-005 example

This template exercises the lifecycle of the fixed
[CT-005 API](https://github.com/YuChia-Wei/ArchPrecept/blob/fdc1f9ff3934c769047f797803abc8614290e889/docs/product/event-sourcing-contract.md)
and [ES implementation](https://github.com/YuChia-Wei/ArchPrecept/blob/fdc1f9ff3934c769047f797803abc8614290e889/src/Contracts/ArchPrecept.Contracts.Domain.EventSourcing/EsAggregateRoot.cs).
The three cases cover committed state after replay, confirmation of a pending
batch, and rejection of reuse after failed replay. The append outcome is
represented by the caller's confirmation step. Event-store atomicity and
transport recovery are outside these cases.

Use the .NET 8 runtime and supply the exact published assemblies from
ArchPrecept.Contracts.Domain and ArchPrecept.Contracts.Domain.EventSourcing
`0.0.3-preview`. The [owner's release record](https://github.com/YuChia-Wei/ArchPrecept/blob/main/docs/releases/0.0.3-preview.md)
records build source `fdc1f9ff3934c769047f797803abc8614290e889` and the following
package digests.

| Exact package | SHA-256 |
| --- | --- |
| ArchPrecept.Contracts.Domain.0.0.3-preview.nupkg | `ceb5c5985a0ee61a00572dc6948ab9b187fe2c6d557249f0482626b0f62e3026` |
| ArchPrecept.Contracts.Domain.EventSourcing.0.0.3-preview.nupkg | `a0a222ada35ecbc4787b69f9a900640bc4469fe847c7144040799710a710c74d` |

The [published build artifact](https://github.com/YuChia-Wei/ArchPrecept/actions/runs/39812215279/artifacts/12441085472)
has ZIP digest `d07b031ee633859b604f007abd20ecca682104f4a723bfb1a9e552cf01712c7b`.
Verify the two packages, preserve their licenses, and extract them into
`domain/` and `eventsourcing/` under an explicit local directory. The generated
project requires both `lib/net8.0` DLLs and restores the test runner dependencies
through ordinary NuGet configuration.

Use the isolated hive registered above.

```powershell
$output = Join-Path $work.FullName 'published-ct005'
$publishedContracts = (Resolve-Path '<verified-extracted-directory>').Path
dotnet new aicf-ct005-contract-tests --name Sample.Ct005Contracts --output $output --debug:custom-hive $hive
dotnet test (Join-Path $output 'Sample.Ct005Contracts.csproj') -c Release "-p:PublishedContractsDir=$publishedContracts"
```

# Analyzer Integration Report

## Metadata

- `workflow_id`: `2026-07-13-critical-remediation-and-analyzer-integration`
- `task_id`: `DEV-002`
- `owner_skill`: `slice-implementer`
- `mode`: `generic-remediation`
- `status`: `final`
- `created_at`: `2026-07-13T22:49:30+08:00`
- `updated_at`: `2026-07-13T22:52:24+08:00`

## Integration Decision

- Apply `DotnetBackendAnalyzers` to production projects through `src/Directory.Build.props`.
- Use an analyzer-only project reference with `OutputItemType="Analyzer"`, `ReferenceOutputAssembly="false"`, and `PrivateAssets="all"`.
- Keep the shared configuration under `src/`, not the repository root, so `tools/` cannot self-reference and tests do not receive architecture diagnostics intended for product code.
- Add the analyzer-enabled product build to the required quick repository gate. Analyzer self-tests remain a separate check.
- Do not reference `DotnetBackendValidation` from product runtime code. Its EF projection-registration helper is currently not applicable to this Dapper-based product and remains independently tested.

## Diagnostic Inventory

The first analyzer-enabled product build failed as intended and proved the analyzer was executing against `src/`:

| Diagnostic | Initial result | Staged policy | Durable owner |
| --- | ---: | --- | --- |
| `DBA1001` | 4 blocking findings on the first build; 5 visible findings after dependent projects compiled | Warning until ARC-003 resolves; then restore error | `ARC-003` |
| `DBA1015` | 36 blocking Use Case contract findings | Warning until ARC-004/DEV-008 resolves; then restore error | `ARC-004` |
| `DBA1017` | 2 blocking Handler boundary findings | Warning until ARC-004/DEV-008 resolves; then restore error | `ARC-004` |

After the explicit staged severities were applied, `dotnet build MQArchLab.slnx --no-restore` succeeded with 53 warnings and zero errors. No diagnostic was suppressed with `NoWarn`; existing architecture debt remains visible in normal builds.

Other important build evidence:

- `DBA1009` stays at its analyzer-default warning severity and does not replace the state-transition tests required by ARC-002.
- NuGet audit confirmed `Microsoft.OpenApi` 2.0.0 as a known high-severity vulnerability through `Microsoft.AspNetCore.OpenApi` 10.0.7 in all three Web APIs and `SaleOrders.Tests`. SEC-001 and DEV-009 own the separate bounded dependency fix.

## Runtime Dependency Boundary

The analyzer reference is build-time only. Product projects do not reference the analyzer output assembly as a normal runtime dependency. Validation must confirm generated product `.deps.json` files do not list `DotnetBackendAnalyzers`.

`DotnetBackendValidation` currently validates EF projection model registration. The product uses Dapper/Npgsql and has no matching EF `DbContext`/projection marker surface, so a production reference would create a meaningless runtime dependency and false assurance.

## Validation

- `dotnet build MQArchLab.slnx --no-restore`: passed after staged severity policy; analyzer diagnostics were emitted from production source.
- `dotnet test tools/DotnetBackendAnalyzers.Tests/DotnetBackendAnalyzers.Tests.csproj --no-restore`: required.
- `dotnet test tools/DotnetBackendValidation.Tests/DotnetBackendValidation.Tests.csproj --no-restore`: required, tool-only applicability.
- Runtime dependency scan of product `.deps.json`: required.
- `check-all.sh --quick`: required after the product analyzer build is added to the gate.

## Deferred Work

- ARC-003 restores `DBA1001` to error after repository/CQRS migration.
- ARC-004 and DEV-008 restore `DBA1015` and `DBA1017` to error after bounded-context migrations.
- SEC-001 and DEV-009 remove the confirmed high-severity transitive OpenAPI vulnerability.
- CI workflow creation is recommended but deferred until TEST-002 defines a deterministic product-test strategy; the local required gate now owns analyzer enforcement.

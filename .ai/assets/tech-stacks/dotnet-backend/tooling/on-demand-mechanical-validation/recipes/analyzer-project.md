# Target-Owned Analyzer Project Recipe

Evidence tier: `reference-only`.

This recipe does not supply an analyzer implementation or select an SDK,
target framework, Roslyn version, package source, or compatibility range. Use it
only after a target owner selects a bounded diagnostic subset from
[`../diagnostic-mapping.yaml`](../diagnostic-mapping.yaml).

## Project Creation Shape

The target may create its own analyzer project with a project file shaped like
the following. Every placeholder is a target decision; the snippet is not a
buildable framework asset.

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>{{target-owned-tfm}}</TargetFramework>
    <IsPackable>{{target-owned-packaging-decision}}</IsPackable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.CodeAnalysis.CSharp"
                      Version="{{target-owned-roslyn-version}}"
                      PrivateAssets="all" />
  </ItemGroup>
</Project>
```

The target must implement positive, negative, exception, and false-positive
tests for each selected rule. DBA labels are compatibility names only; canonical
standards remain the semantic owners.

## Target Wiring Shape

After the analyzer project exists and its tests pass, the target may wire it to
selected projects:

```xml
<Project>
  <ItemGroup Condition="Exists('{{target-owned-analyzer-project}}')">
    <ProjectReference Include="{{target-owned-analyzer-project}}"
                      OutputItemType="Analyzer"
                      ReferenceOutputAssembly="false"
                      PrivateAssets="all" />
  </ItemGroup>
</Project>
```

The target owns which projects receive the reference and whether a missing
analyzer path fails the build. A broad `Directory.Build.props` reference is not
the framework default.

## Evidence Required For An Active Claim

- target decision naming selected diagnostics and exceptions;
- exact project, SDK, target framework, Roslyn, and test package versions;
- implementation and test commit;
- applied project wiring and severity configuration;
- exact build/test/CI command outcomes against the claimed target commit; and
- a compatibility and rollback statement.

Without all of that evidence, report the recipe as `not-selected` or the target
implementation as `unresolved`; do not infer activation from this directory.

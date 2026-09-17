# Runnable GWT Step-Method Example

Read a test body as a scenario: business data in Given, a single real query in
When, and explicit observable assertions in Then. Construction and substitute
mechanics live in private methods. The two test projects implement the same
[scenario and assertion mapping](scenarios.md) with different explicitly
selected GWT orchestration profiles.

- [Default BDDfy tests](DefaultBddfy/BudgetQueryTests.cs) use a fluent step chain
  and captured per-test results.
- [Plain xUnit tests](PlainXunit/BudgetQueryTests.cs) demonstrate this example's
  explicit BDDfy opt-out, with method calls and returned results.
- [BudgetQuery.cs](BudgetQuery.cs) is the original bounded example subject. Its
  complete behavior and exclusions are defined in `scenarios.md`; it is not a
  production budgeting library or a copy of either historical classroom project.

The canonical [test standard](../../standards/coding-standards/test-standards.md)
owns method responsibilities, async/exception behavior and target selection.
The [GWT handoff contract](../../../../shared/GWT-TEST-HANDOFF-CONTRACT.md)
owns source/scenario/implementation traceability. This example illustrates those
contracts; it does not override them or select packages for other targets.

## Build And Run

These are optional teaching projects, excluded from the framework core's
SDK-free project inventory. Framework setup and required validation do not
build or run them; use the commands below only when choosing to execute this
example. The exception is scoped to this directory.

Prerequisite: a .NET SDK capable of targeting .NET 8, the .NET 8 runtime, and
access to the explicitly configured public NuGet feed on the first restore.
Run from this directory:

```text
dotnet build DefaultBddfy/DefaultBddfy.csproj
dotnet test DefaultBddfy/DefaultBddfy.csproj --no-build --logger "trx;LogFileName=default.trx"
dotnet build PlainXunit/PlainXunit.csproj
dotnet test PlainXunit/PlainXunit.csproj --no-build --logger "trx;LogFileName=plain.trx"
```

Expect **five passed cases per project**, with both BUDGET-02 rows visible in
the result. Build/test artifacts remain in `bin`, `obj` and `TestResults`; do not
commit them. Record the actual revision, command, profile, discovered cases and
results when using these commands as evidence. A successful command with zero
tests is not a passing example.

`Directory.Build.props` pins xUnit v3 3.2.2, the VSTest runner 4.0.0, Test SDK
18.10.0 and NSubstitute 6.2.0 for this fixture. The default project additionally
pins TestStack.BDDfy 10.0.13; the plain project has no BDDfy reference. These are
fixture selections, not a request to upgrade a target's existing stack.

Package/API references: [BDDfy](https://www.nuget.org/packages/TestStack.BDDfy/10.0.13),
[xUnit v3](https://www.nuget.org/packages/xunit.v3/3.2.2),
[xUnit VSTest runner](https://www.nuget.org/packages/xunit.runner.visualstudio/4.0.0),
[Test SDK](https://www.nuget.org/packages/Microsoft.NET.Test.Sdk/18.10.0),
[NSubstitute](https://www.nuget.org/packages/NSubstitute/6.2.0), and
[xUnit execution guidance](https://xunit.net/docs/getting-started/v3/getting-started).

## Reuse In A Target

Keep the target's real behavior and approved technology choices. Carry scenario
IDs and every Then outcome into the test/step/assertion mapping. Use the examples
for structure, replacing the fixture subject and dependency with the target's
actual boundaries. Review the called step bodies and execute the resulting
tests; copying the method names does not establish scenario fidelity.

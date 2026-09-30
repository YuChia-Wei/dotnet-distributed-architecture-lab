# Development Tools and Common Commands Guide (.NET)

## Applicability

This optional .NET reference applies only to the target-selected architecture,
providers and adopted test rules. Examples do not install packages, select an ORM,
broker or Event Sourcing, create fixed project paths, or prove execution. Preserve
per-domain persistence decisions and the target-selected GWT contract; BDDfy and
mocking packages remain separately selected.

## 📋 Overview

Provides a reference for common tools and commands used in .NET projects.

## 🛠️ .NET CLI Commands

### Basic Commands
```bash
# Build the project
dotnet build

# Run all tests
dotnet test

# Run a specific test class
dotnet test --filter FullyQualifiedName~<TestClass>

# Run a specific test method
dotnet test --filter FullyQualifiedName~<TestClass>&FullyQualifiedName~<TestMethod>

# Publish without running tests
dotnet publish -c Release -p:RunTests=false

# Watch and rebuild
dotnet watch --project <HostProject>
```

### Dependency Management
```bash
dotnet list package
dotnet add package <SelectedPackage>
dotnet restore
```

## Git and change authority

Use the target project's actual commit grammar, branch/PR topology and authorized
integration operations. `git status`, `git diff` and `git log` help inspect state;
a command example does not authorize staging, pushing, merging or changing main.
For cross-machine continuation, preserve a durable checkpoint under the target's
selected workflow and provider rules. This package has no source Git-policy path
or mandatory workflow branch convention.

## Commit Conventions
```
feat: Add a feature
fix: Fix a defect
docs: Update documentation
style: Adjust formatting
refactor: Refactor code
perf: Improve performance
test: Add tests
chore: Adjust supporting tools
```

## 🗃️ EF Core Migration Commands
```bash
dotnet ef migrations add <MigrationName> --project <InfrastructureProject> --startup-project <HostProject>
dotnet ef database update --project <InfrastructureProject> --startup-project <HostProject>
```

## 🔧 IDE Shortcuts

### Visual Studio
```
Ctrl + T           # Go to All
Ctrl + .           # Quick Actions
F12                # Go to Definition
Ctrl + Shift + F   # Find in Files
```

### VS Code
```
Cmd + P            # Quick Open
Cmd + Shift + P    # Command Palette
Cmd + Shift + F    # Find in Files
F12                # Go to Definition
```

## 🐛 Debugging Tips

```bash
dotnet watch --project <HostProject>
```

### Adjusting Log Levels
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Debug",
      "Microsoft": "Warning"
    }
  }
}
```

## 🚀 Performance Analysis

```bash
dotnet-counters monitor --process-id <pid>
dotnet-trace collect --process-id <pid>
```

## 🔗 Related Resources

- Target-owned Git flow and commit policy (caller-supplied authority).
- Target-owned Git flow and commit policy (caller-supplied authority).
- [Database migration guide](DATABASE-MIGRATION-GUIDE.md)
- [Microsoft .NET documentation](https://learn.microsoft.com/dotnet)
- [Microsoft EF Core documentation](https://learn.microsoft.com/ef/core)

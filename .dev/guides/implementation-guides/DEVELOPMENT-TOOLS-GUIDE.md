# Development Tools and Common Commands Guide (.NET)

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

## 🔍 Git Commands

```bash
git status
git switch main
git switch -c codex/<workflow-id>
git add -A
git commit -m "feat: Add new feature"
git push -u origin codex/<workflow-id>
git switch main
git merge --no-ff codex/<workflow-id>
git push origin main
```

When an incomplete workflow needs a cross-machine handoff, prefer pushing the workflow branch. If the user explicitly requests an interim merge, still use `--no-ff` and record it as a checkpoint; then create a new continuation branch from the updated `main` when work resumes.

### Commit Conventions
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

- [Git flow rules](../../TEAM-GIT-FLOW-RULES.MD)
- [Git commit policy](../../standards/GIT-COMMIT-POLICY.md)
- [Database migration guide](DATABASE-MIGRATION-GUIDE.md)
- [Microsoft .NET documentation](https://learn.microsoft.com/dotnet)
- [Microsoft EF Core documentation](https://learn.microsoft.com/ef/core)

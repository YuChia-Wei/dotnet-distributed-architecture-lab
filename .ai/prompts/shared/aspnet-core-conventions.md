# ASP.NET Core Conventions (Dotnet)

## Main Application Entry Rules

### 1) Single Entry Point
- There must be exactly **one** ASP.NET Core entry point.
- Prefer `src/Api/Program.cs` as the single entry.
- Do not create duplicate `Program.cs` or multiple `WebApplication` builders.

### 2) Naming and Location
- Project name example: `Api` or `{ProjectName}.Api`.
- Keep `Program.cs` at project root (same folder as `.csproj`).
- If using top-level statements, expose a `partial class Program` for testing.

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
// TODO: register application services explicitly (no assembly scanning)

var app = builder.Build();
app.MapControllers();
app.Run();

public partial class Program { }
```

### 3) Environment Configuration
- Use `ASPNETCORE_ENVIRONMENT` for profile switching.
- Use `appsettings.{Environment}.json` for environment overrides.
- Do not hardcode environment in tests.

Priority order:
1) `appsettings.{Environment}.json`
2) environment variables
3) `appsettings.json`

### 4) DI Conventions
- Explicit registration only; no implicit scan rules.
- Use clear module-level registration (e.g., `services.AddApplication()` wrappers).

### 5) Test Conventions
- `WebApplicationFactory<Program>` should target the **single** entry point.
- If tests fail to find `Program`, ensure `public partial class Program { }` exists.

## Pre-Generation Checklist
1) Check existing `Program.cs` and `.csproj` location.
2) Ensure only one entry point.
3) Confirm `Program` is accessible to tests.
4) Ensure environment config uses appsettings files.

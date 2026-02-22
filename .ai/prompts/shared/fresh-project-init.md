# Fresh Project Initialization Guide (Dotnet)

## When to Use
For brand new .NET projects without an existing API host.
For full profile/outbox setup, delegate to `profile-config-sub-agent`.

## Step 0: Check Project State
```bash
# check for existing Program.cs
find . -name "Program.cs"
```
If an entry point exists, reuse it. Do not create duplicates.

## Step 1: Create ASP.NET Core App (if missing)
Use the conventions in `./aspnet-core-conventions.md`.
Ensure a single `Program.cs` with explicit DI registration.

## Step 2: Create Essential Common Classes (if missing)
- **DateProvider** (unified time source)

TODO: finalize .NET DateProvider location and API surface.

## Step 3: Create Basic Configuration Files
```json
// appsettings.json
{
  "App": { "Name": "aiscrum" }
}
```

```json
// appsettings.TestInMemory.json
{
  "App": { "Mode": "inmemory" }
}
```

```json
// appsettings.TestOutbox.json
{
  "App": { "Mode": "outbox" }
}
```

> NOTE: database and environment values must be copied from `.dev/project-config.yaml`.

## Step 4: Basic DI Registration
```csharp
// TODO: create service registration modules
// services.AddApplication();
// services.AddInfrastructure(configuration);
```

## Step 5: Messaging / Outbox (if needed)
- Use WolverineFx for CQRS/MQ/Event Sourcing.
- Use EF Core for ORM and outbox persistence.

TODO: map connection-frame configs to WolverineFx pipelines.

## Order of Execution
1) Verify project entry point exists
2) Add basic config files
3) Add essential common classes
4) Register DI modules
5) Delegate advanced profiles/outbox to `profile-config-sub-agent`

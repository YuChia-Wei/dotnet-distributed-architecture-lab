# Repo Scan Playbook

Use this reference to rebuild architecture truth from a newly copied target repository.

## Evidence Order

Prefer sources in this order:

1. repository file tree
2. `*.sln`, `*.csproj`, `Directory.Packages.props`, `global.json`
3. deployment and infra config
4. existing repo README / docs
5. copied template docs that may now be stale

## Minimum Scan Checklist

Capture these facts before editing:

- top-level directories
- solution names and project count
- executable projects versus libraries
- primary source roots such as `src/`, `tests/`, `apps/`, `services/`
- shared kernel or building-block projects
- test frameworks and test project naming
- database, ORM, message broker, and API host packages
- container or deployment folders

## .NET Structure Hints

When the repo is .NET-based, inspect:

- target framework from `TargetFramework` or `TargetFrameworks`
- package references for EF Core, Dapper, Npgsql, Wolverine, MassTransit, MediatR, xUnit, NUnit, MSTest
- project names and folders for API, worker, consumer, contracts, shared libraries
- solution folders or naming patterns that imply bounded contexts

## Safe Inference Rules

- Folder names alone are weak evidence.
- `*.csproj` plus package references are stronger evidence.
- Startup or host projects are stronger than class library names.
- If multiple patterns exist, summarize the mixed state instead of forcing one architecture label.

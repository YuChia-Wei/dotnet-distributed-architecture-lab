# Tech Stack AI Context

This folder contains agent-facing context that is reusable only within a specific technology stack profile.

Use this folder when a rule is not project-specific but also not universal across stacks.

## Profiles

- `dotnet-backend/`
  - .NET backend-only AI context.
  - Excludes Razor, Blazor, MAUI, ASP.NET MVC view rendering, and other .NET frontend UI frameworks.

Universal context remains under `.ai/assets/shared/`.

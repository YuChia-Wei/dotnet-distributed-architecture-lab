# CORS Setup (Dotnet)

## Quick Fix
Configure CORS in `src/Api/Program.cs` (or `src/Api/Extensions/CorsExtensions.cs`).

- AllowedOrigins: `http://localhost:5173`
- ExposedHeaders: `Location`, `Operation-Id`, `traceId`

Example:
```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddCors(options =>
{
    options.AddPolicy("Frontend", policy =>
    {
        policy.WithOrigins("http://localhost:5173")
            .AllowAnyHeader()
            .AllowAnyMethod()
            .WithExposedHeaders("Location", "Operation-Id", "traceId");
    });
});

var app = builder.Build();
app.UseCors("Frontend");
```

See: `.ai/assets/shared/common-rules.md` for shared rules.

## Status
✅ Implemented in this project (verify if port differs).



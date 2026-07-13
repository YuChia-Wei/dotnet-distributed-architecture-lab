# CORS Setup (.NET)

## Applicability

Use this guide when the target repository exposes an ASP.NET Core HTTP host to a browser client. Confirm the host project, composition-root path, policy name, allowed origins, and exposed headers from target-repository evidence before applying the example.

Do not infer a frontend, a fixed host path, or a deployed origin from this context framework. If `.dev/project-config.yaml` exists, treat it as a summary of discovered evidence rather than an authority that overrides project files.

## Example

Configure CORS in the target host's composition root or an extension called by it.

- Allowed origins: load from configuration such as `Cors:AllowedOrigins` or an environment-specific secret/configuration source.
- Exposed headers: include only headers the target API actually returns and browser clients must read.

```csharp
var builder = WebApplication.CreateBuilder(args);
var allowedOrigins = builder.Configuration
    .GetSection("Cors:AllowedOrigins")
    .Get<string[]>() ?? [];

builder.Services.AddCors(options =>
{
    options.AddPolicy("BrowserClient", policy =>
    {
        policy.WithOrigins(allowedOrigins)
            .AllowAnyHeader()
            .AllowAnyMethod()
            .WithExposedHeaders("Location");
    });
});

var app = builder.Build();
app.UseCors("BrowserClient");
```

Adapt the policy name, headers, methods, and origin source to the target repository. Do not combine credentialed requests with wildcard origins.

See `.ai/assets/tech-stacks/dotnet-backend/shared/common-rules.md` for shared rules.

## Verification

1. Confirm the middleware is registered in the target HTTP host and ordered correctly for its pipeline.
2. Confirm every allowed origin comes from reviewed configuration.
3. Exercise an allowed and a disallowed preflight request in the target repository's normal validation environment.
4. Record deployment-specific origins outside reusable templates.

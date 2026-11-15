# ASP.NET Core Web API setup

Use this reference for an actual ASP.NET Core HTTP host. Confirm the target's
SDK, host, endpoint contracts and selected application or infrastructure
boundaries. The [API starters](../../tooling/generation/README.md) offer sample
routes and behavior for a chosen template. Adapt them to the target.

## Compose and verify startup

1. Configure the [host environment](../../core/host-configuration.md), add the
   actual transport, bind and validate required options, and invoke the
   selected registration modules. Use the target's secret provider.
2. Register and map the selected controllers or endpoints. Order middleware
   according to the actual routing, access and error policy. Verify the
   [HTTP contract](controller-standards.md) at its real entry point.
3. Where [persistence](../../integration/persistence/configuration.md) is
   selected, confirm provider packages, actual connection/port, schema,
   mappings and migration ownership. Check that the deployed environment uses
   the intended configuration. Where messaging is selected, check
   subscriptions, provider/adapter registration and the [transaction/delivery
   contract](../../integration/messaging/transactional-messaging-standards.md).
4. Exercise startup and a real route through the target's smoke or integration
   check. For the route, observe status, response/body and failure behavior.
   If the target supports multiple environments, use the intended host and
   [test profile](../../testing/profile-based-testing.md) for each claim.

For example, a browser-facing host may store shared logging defaults in
`appsettings.json` and a deployment's origin list under `Cors:AllowedOrigins`
in `appsettings.{Environment}.json`. Use the host's actual endpoints and
settings keys. The JSON provider alone does not expand `${...}` placeholders.

## CORS for a browser client

Confirm the actual browser origin, methods, request headers, exposed response
headers and whether credentials are required. Use explicit reviewed origins
when credentials are allowed. Expose `Location`, for example, only when clients
need to read it. A non-browser endpoint need not add a CORS policy solely
because it uses ASP.NET Core.

For an endpoint-routed host that explicitly calls `UseRouting`, a named policy
normally runs after routing and before authorization and endpoint execution.
Confirm the actual pipeline and any endpoint-specific policy selection. The
configuration example uses exact allowed origins:

```csharp
var allowedOrigins = builder.Configuration
    .GetSection("Cors:AllowedOrigins")
    .Get<string[]>() ?? [];

builder.Services.AddCors(options =>
{
    options.AddPolicy("BrowserClient", policy =>
        policy.WithOrigins(allowedOrigins)
              .WithMethods("GET", "POST")
              .WithHeaders("Content-Type")
              .WithExposedHeaders("Location"));
});
```

Apply the policy in the target pipeline. Exercise a preflight from an allowed
origin and from an origin or method that is disallowed. Check the returned
CORS headers and confirm the browser sees only the approved responses. CORS
configuration does not establish authentication or access authorization.

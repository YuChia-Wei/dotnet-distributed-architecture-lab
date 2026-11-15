# .NET host configuration

Read the actual host builder, configuration sources, deployment settings and
registration entry point. An environment and its settings select configuration
values for that host. They do not identify a database, messaging provider or
domain architecture by themselves.

## Adopted environment profile

The existing environment profile uses a single host-selected environment from
`DOTNET_ENVIRONMENT` or `ASPNETCORE_ENVIRONMENT`. Inspect the selected builder's
precedence and use its resolved environment name. Set the appropriate variable
at the launch boundary. Do not add a custom `Profile` selector, a `.feature`
selector, a list of environments or application code that overrides the process
environment. Avoid setting the two variables to conflicting values.

Keep shared defaults in `appsettings.json`. Put environment-specific JSON
overrides in `appsettings.{Environment}.json`, preserving the host's expected
configuration precedence for secrets, environment variables and command-line
values. With the standard host builder use its normal configuration pipeline.
If a target explicitly builds that pipeline, preserve the base-before-override
order and any higher-priority sources. `${...}` in JSON needs a deliberately
selected expansion mechanism. Keep secret values in the target's secret store
or environment configuration.

Use the adopted names and exact casing throughout settings filenames, launch
commands and registrations. The existing vocabulary is `Development`,
`Production`, `InMemory`, `Outbox`, `TestInMemory` and `TestOutbox` where those
environments are supported. A target that has only one persistence option does
not need to introduce a second profile.

## Composition

Centralize differences in the composition root or an explicitly called
registration module. For the adopted profile, make each branch explicit with
`IServiceCollection` registration and keep profile selection out of services.
Assembly or attribute scanning cannot replace explicit profile branches.
General services depend on the required abstraction rather than a concrete
profile-specific infrastructure type. Validate required configuration and
registrations at startup so an incomplete profile fails before first use.

For example, use `builder.Environment.EnvironmentName` with the accepted
configuration pipeline and use `builder.Environment.IsEnvironment("TestOutbox")`
only where the target selected that exact environment. See [persistence
composition](../integration/persistence/configuration.md) for the selected
dual-provider branch and [test fixture ownership](../testing/profile-based-testing.md)
for isolated test selection.

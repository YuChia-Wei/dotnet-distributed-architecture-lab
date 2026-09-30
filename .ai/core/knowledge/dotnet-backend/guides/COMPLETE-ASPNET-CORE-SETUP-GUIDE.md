# ASP.NET Core setup reference

## Applicability

This optional .NET reference applies only to the target-selected architecture,
providers and adopted test rules. Examples do not install packages, select an ORM,
broker or Event Sourcing, create fixed project paths, or prove execution. Preserve
per-domain persistence decisions and the target-selected GWT contract; BDDfy and
mocking packages remain separately selected.

Use this optional checklist only for an ASP.NET Core target. It is an example
assembly route, not a verified complete application or a package installation
instruction. Preserve target-selected versions, architecture, persistence,
broker, testing and deployment decisions.

## Select the parts that exist in the target

1. Confirm the solution's actual host, application/domain and infrastructure
   boundaries. [Project structure](../standards/project-structure.md) illustrates
   one adopted layout; it is not a mandatory scaffold.
2. Confirm framework/dependency versions from target project and lock files.
   EF Core, Wolverine and xUnit/BDDfy are example choices, not a required bundle.
3. Configure only selected providers. Use the target's configuration/secret
   mechanism; `${...}` placeholders require explicit application/container
   expansion and are not automatically expanded by ASP.NET Core JSON loading.
4. Check registration and startup through the target's selected smoke or DI test.
   An available template is not evidence that its startup succeeds.
5. If the target selects an outbox or Event Sourcing, separately check persistence,
   transaction boundaries, delivery and replay semantics. Do not infer either
   pattern from CQRS or from a profile name.

## Packaged examples

- [ASP.NET Core host examples](../examples/aspnet-core/README.md)
- [Outbox examples](../examples/outbox/README.md)
- [Persistence registration guidance](PERSISTENCE-CONFIGURATION-GUIDE.md)
- [Profile testing guidance](PROFILE-BASED-TESTING-GUIDE.md)

Examples are reference code, not a source-repository project or an already
executed install. Fill target-specific values and validate the selected route.

# .NET knowledge

This optional package supplies common C# and .NET guidance, ASP.NET Core Web API
references, and resources for selected architecture, integration and test
profiles. Read the target's actual project files, configuration, adopted
decisions and applicable standards before choosing a resource.

Use only the task-relevant resource IDs allowed by the installed selection and
the consuming skill. A link aids navigation within that boundary. Required
inputs must be available before their associated operation can proceed.
`target-authority:<name>` denotes an explicitly supplied target-owned input.
Member links are relative to their document, rule owner paths to the catalog,
and embedded rule text uses its semantic owner's link base.

| Task | Start here |
| --- | --- |
| Establish runtime, language and style | [Technology selection](core/technology-selection.md), [C# conventions](core/csharp-conventions.md) |
| Configure a host | [Host configuration](core/host-configuration.md) |
| Review preconditions, invariants or postconditions | [Design by Contract](core/design-by-contract.md) for adopted contracts |
| Build or review an ASP.NET Core HTTP surface | [Setup](application-types/web-api/setup.md), [Controller standards](application-types/web-api/controller-standards.md) |
| Design or implement the selected DDD/CQRS architecture | [Overview](architecture/ddd-cqrs/overview.md), then the relevant boundary |
| Work with a persistence adapter or read model | [Configuration](integration/persistence/configuration.md), then the applicable port or mapping contract |
| Configure messaging or verify local atomicity | [Persistence and messaging](integration/messaging/persistence-and-messaging.md), [Transactional messaging](integration/messaging/transactional-messaging-standards.md) |
| Design or implement a test | [Test standards](testing/test-standards.md), [Profile testing](testing/profile-based-testing.md) where selected |
| Develop from a specification or interface without an IDE | [Low-dependency development workflow](tooling/development-tools.md) |
| Generate editable source | [Generation guide](tooling/generation/README.md) |
| Diagnose an observed failure | [Troubleshooting](references/troubleshooting.md) |

The package depends on `engineering-common@0.4.2`. Use the
[rule catalog](engineering-rule-catalog.yaml) and [identity
bindings](references/engineering-identity-bindings.md) to identify retained rule
IDs and their conditions. `dotnet@0.3.0` replaces the previous package identity.
Targets that selected `dotnet-backend` must explicitly migrate their package
and resource selection. This package supplies no automatic aliases. Existing
`dotnet-backend` technology-profile tokens identify their original adoption
scope. Target owners retain per-domain persistence choices, ES selection,
style, BDDfy opt-out and mocking decisions. See [policy
rationale](references/policy-rationale.md) for provenance and unresolved choices.

[Mechanical validation materials](tooling/on-demand-mechanical-validation/README.md)
are reference-only. A target with a verified legacy .NET compliance adoption
can explicitly select the [legacy gate
rules](references/legacy-dotnet-compliance/spec-compliance-rules.md),
[validation steps](references/legacy-dotnet-compliance/test-validation-steps.md)
and [command examples](references/legacy-dotnet-compliance/validation-command-templates.md)
for its compatible format. The legacy helper is unavailable until the target
can resolve its original supported route.

## Migrating from 0.1.9 examples

The 0.2 line removed the old `examples/` and `source-includes/` trees. Update
project-owned links explicitly and treat previously generated code as ordinary
target-owned code.

| Previous content | Current entry or disposition |
| --- | --- |
| `examples/usecase`, `examples/use-case-injection` | `aicf-usecase` plus [Use Case guidance](architecture/ddd-cqrs/usecase-standards.md); registrations belong to the target |
| `examples/aspnet-core`, `examples/controller`, `examples/dto` | `aicf-miniapi` or `aicf-webapi` reference feature; adapt HTTP contracts to the target |
| `examples/generation-templates`, `examples/reference`, `examples/profile-configs` | [Generation guide](tooling/generation/README.md) for native API starters, C# items and snippets |
| `source-includes/domain`, `examples/aggregate` | `domain-contracts` and optional `es-aggregate` snippets, selected by the adopted contract |
| `examples/contract`, `examples/mapper` | [DbC](core/design-by-contract.md), [mapping](integration/persistence/mapper-standards.md) and [reconstruction cases](testing/reconstruction-and-projector-cases.md) |
| `examples/bdd-gherkin-example`, `examples/bdd-given-when-then-example`, `examples/bdd-step-methods` | Generic Gherkin in `engineering-common/bdd`; implement and verify business bindings locally |
| `examples/outbox`, `examples/projection`, `examples/inquiry-archive`, `examples/nuget` | Selected persistence, messaging and package guidance; use the target's own integration implementation |

The separate generation bundle supplies starters, snippets and
[domain contract test templates](testing/domain-contract-examples.md). Compile
and validate the adapted result in the target.

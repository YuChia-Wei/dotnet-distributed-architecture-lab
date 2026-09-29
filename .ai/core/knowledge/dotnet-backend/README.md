# .NET Backend Knowledge

This optional content package supplies reusable engineering references. Installation
makes content available; it does not adopt rules, select technology, activate a
skill/worker, run tools, or copy examples/source includes into product code.

Load task-relevant resource IDs through the explicit installed selection and the
target-owned authority. Missing authority or specialist coverage remains unresolved;
no source-checkout fallback is allowed. The content metadata describes availability,
not runtime execution. Resource/member references are relative to the containing
member; catalog owner paths are relative to the catalog at the package root.
Embedded normative Markdown uses its declared semantic owner's relative base.

`target-authority:<name>` is a descriptive input parameter, not a path or executable
command. The caller must supply the matching target-owned method, policy or tool
through its existing binding. A source-provenance marker is inert history and must
never be loaded as an installed dependency. Target project paths in illustrative
layouts/configuration examples refer only to the target and are not bundled inputs.

## Scope

Included:

- DDD, Clean Architecture, CQRS, and Hexagonal Architecture backend rules
- ASP.NET Core backend host configuration
- command, query, reactor, aggregate, repository, projection, and controller patterns
- Dapper, EF Core, PostgreSQL, WolverineFx, RabbitMQ, Kafka, Outbox, and Event Sourcing guidance
- xUnit Given-When-Then testing rules, with BDDfy and NSubstitute as overridable profile defaults and optional `.feature` support

Excluded:

- Razor
- Blazor
- MAUI
- ASP.NET MVC view rendering
- frontend UI component generation
- full-stack or mono-system template rules

## Adoption and coverage

Requires `engineering-common@0.1.0`. Preserve per-domain persistence and transaction
choices, conditional Event Sourcing, explicit BDDfy opt-out and target-selected
mocking. No file extension or example automatically selects a technology.

The catalog retains 11 registered rule identities and 11 unregistered guidance
documents. Unregistered guidance does not claim normative rule coverage. Legacy
role projections are technical references only. Examples, source includes and
mechanical-validation recipes require separately selected target verification.
Historical evidence and obsolete forwarding files are excluded.

## Contents

The metadata lists every member and resource. The following links are topic entrypoints;
select additional resources by their declared IDs for the current task.

- Content metadata: `content-package.yaml`
- [design/architecture-playbook.md](design/architecture-playbook.md)
- [design/design-routing.yaml](design/design-routing.yaml)
- [engineering-rule-catalog.yaml](engineering-rule-catalog.yaml)
- [examples/aggregate/README.md](examples/aggregate/README.md)
- [examples/bdd-given-when-then-example/README.md](examples/bdd-given-when-then-example/README.md)
- [examples/usecase/README.md](examples/usecase/README.md)
- [guides/TEMPLATE-USAGE-GUIDE.md](guides/TEMPLATE-USAGE-GUIDE.md)
- [references/BUILDING-BLOCKS-CLASS-INDEX.MD](references/BUILDING-BLOCKS-CLASS-INDEX.MD)
- [references/CODE-TEMPLATES.MD](references/CODE-TEMPLATES.MD)
- [review/review-routing.yaml](review/review-routing.yaml)
- [shared/testing-strategy.md](shared/testing-strategy.md)
- [source-includes/domain/README.md](source-includes/domain/README.md)
- [standards/coding-standards.md](standards/coding-standards.md)
- [standards/project-structure.md](standards/project-structure.md)
- [tooling/on-demand-mechanical-validation/README.md](tooling/on-demand-mechanical-validation/README.md)

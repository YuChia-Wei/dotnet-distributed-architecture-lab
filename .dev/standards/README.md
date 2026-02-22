# .NET CA + WolverineFx + EF Core Tech Stack

This folder contains the .NET adaptation of the source CA ezddd tech stack.
All architecture and development rules (DDD/CA/CQRS, event sourcing, outbox, contract testing, mutation testing) must be preserved.
Use WolverineFx for CQRS/MQ/Event Sourcing, EF Core for ORM, xUnit + BDDfy (Gherkin-style naming) for BDD, and NSubstitute for mocks.

## Structure
- `coding-standards/`: .NET coding rules used by compliance scripts.
- `guides/`: .NET workflow and configuration guides (translated from the source stack).
- `templates/`: reusable configuration/templates (appsettings, profiles, project config).
- `examples/`: code templates and reference examples.
- `prompts/`: prompt templates for AI-assisted changes.

## Notes
- ezDDD/ezSpec concepts must be preserved even without direct .NET packages.
- If no .NET equivalent exists, keep the rule and mark TODO rather than deleting it.

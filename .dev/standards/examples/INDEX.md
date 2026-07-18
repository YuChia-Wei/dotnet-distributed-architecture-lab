# Examples Index

This file is the navigation catalog for `.dev/standards/examples/`.
Evidence strength comes from
[`evidence-manifest.yaml`](evidence-manifest.yaml), not from placement in this
directory.
Placeholder/API disposition comes from
[`placeholder-disposition.yaml`](placeholder-disposition.yaml).

## Current Illustrations

- [`aggregate/`](aggregate/) — Aggregate, Entity, Value Object, and event
  illustrations aligned to the optional `EsAggregateRoot<TId>` contract.
- [`controller/`](controller/) — async ASP.NET Core Controller-to-Use-Case
  boundary.
- [`dto/`](dto/) — DTO placement and shape illustrations.
- [`use-case-injection/`](use-case-injection/) — Use Case injection boundary.

These are illustrative, not standalone copy-ready projects.

## On-Demand References

- [`aspnet-core/`](aspnet-core/) — conditional runtime/profile configuration.
- [`bdd-given-when-then-example/`](bdd-given-when-then-example/) — BDDfy rule
  mapping.
- [`bdd-gherkin-example/`](bdd-gherkin-example/) — distinct Reqnroll/Gherkin
  feature mode.
- [`generation-templates/`](generation-templates/) — legacy generation inputs,
  not verified generators.
- [`inquiry-archive/`](inquiry-archive/) — query/archive concepts.
- [`mapper/`](mapper/) — mapping concepts and incomplete portfolio examples.
- [`nuget/`](nuget/) — package-layout reference; target versions remain
  target-selected.
- [`outbox/`](outbox/) — Outbox concepts with target-selected adapters.
- [`profile-configs/`](profile-configs/) — historical profile variants.
- [`projection/`](projection/) — projection/read-model concepts.
- [`usecase/`](usecase/) — Use Case lineage and illustrative APIs.

Reference-only folders are loaded when their topic is selected. They are not
active API or package truth.

## Historical Provenance

- [`contract/`](contract/) — uContract/Design-by-Contract source lineage.
- [`reference/`](reference/) — Java, EzDDD, and migration mappings.

## Shared Fixture Ownership

- Hollow shared test-host fixtures were retired rather than promoted into a
  reference product. Target tests construct only the fixtures their real
  infrastructure requires.
- `outbox/OUTBOX-TEST-CONFIGURATION.md` owns the shared
  Outbox test configuration reference.
- `appsettings.InMemory.json` and `appsettings.TestInMemory.json` intentionally
  retain equal values because ASP.NET Core selects sibling environment files by
  exact environment name; this is a semantic alias, not an accidental fixture
  duplicate.

## Maintenance

- Add or change a folder only with an `evidence-manifest.yaml` entry.
- Put file-level details in the folder README.
- Keep this file as the sole root catalog.

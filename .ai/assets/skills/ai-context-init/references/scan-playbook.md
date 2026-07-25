# Repo Init and Scan Playbook

Rule IDs: `AICTX-EVIDENCE-001`, `TECH-SELECT-001`

Use this reference as the first pass after this AI context framework is copied into a target repository.

The goal is repo initialization, not product feature planning. Establish what the target repository actually is, then refresh only the copied context files that depend on repo-specific facts.

## Target Repository Modes

Classify the target before editing:

| Mode | Evidence | First Action |
| --- | --- | --- |
| Empty or near-empty repo | no solution, source, tests, or product docs yet | keep framework rules, create minimal placeholder architecture entries, and ask for stack/product direction before inventing facts |
| Existing repo | source, tests, package files, deployment config, or product docs already exist | rebuild repo-specific truth from file-backed evidence |
| Copied-template repo | framework docs exist with stale source-project names or paths | preserve framework-level rules and rewrite copied project truth |

Do not infer product domains, bounded contexts, queues, routes, or deployment topology for an empty repo.

## Project Config Generation

Use `.ai/assets/skills/ai-context-init/templates/project-config.template.yaml` as the canonical shape for target-repository project facts.

- Generate `.dev/project-config.yaml` only after the inventory pass.
- Populate a field only when repository evidence or user-confirmed truth supports it.
- Keep unknown scalar values as `null` and unknown collections empty.
- Record technology choices under `technologySelections` using
  `templates/technology-selection.schema.yaml`. Do not create package-specific
  top-level selection fields.
- Leave an absent selection slot unresolved so the applicable framework profile
  default can be evaluated separately; record an entry only from repository
  evidence or an explicit target decision.
- Do not copy credentials, connection strings, local ports, database names, queue names, or product identifiers from the source framework repo.
- For an empty repository, either omit `.dev/project-config.yaml` or create the template shape with `generationStatus: not-initialized`; do not invent stack or product facts.
- Record supporting paths under `evidence.files`.

## Evidence Order

Prefer sources in this order:

1. repository file tree
2. `*.sln`, `*.csproj`, `Directory.Packages.props`, `global.json`
3. deployment and infra config
4. existing repo README / docs
5. copied template docs that may now be stale

An optional index, code graph, IDE index, MCP server, or semantic search may
accelerate this inventory but must not become a prerequisite or a new evidence
tier. Before concluding that a root, file type, or documentation relationship is
absent, use the tool-neutral fallback checks in
`.dev/standards/AI-CONTEXT-BOUNDARY.md#tool-neutral-evidence-boundary`. Reopen
the direct files supporting every generated project fact.

## Minimum Scan Checklist

Capture these facts before editing:

- top-level directories
- solution names and project count, if present
- executable projects versus libraries, if present
- primary source roots such as `src/`, `tests/`, `apps/`, `services/`
- shared kernel or building-block projects
- test frameworks and test project naming
- database, ORM, message broker, and API host packages
- explicit target selections or overrides for mocking, BDD runner, ORM,
  database, broker, messaging framework, and observability runtime
- container or deployment folders
- existing `.dev/project-config.yaml` facts that conflict with stronger repository evidence

## .NET Structure Hints

When the repo is .NET-based, inspect:

- target framework from `TargetFramework` or `TargetFrameworks`
- package references for EF Core, Dapper, Npgsql, Wolverine, MassTransit, MediatR, xUnit, NUnit, MSTest
- project names and folders for API, worker, consumer, contracts, shared libraries
- solution folders or naming patterns that imply bounded contexts

## Safe Inference Rules

- Folder names alone are weak evidence.
- `*.csproj` plus package references are stronger evidence.
- Startup or host projects are stronger than class library names.
- If multiple patterns exist, summarize the mixed state instead of forcing one architecture label.
- If no product files exist, preserve the AI context framework and mark product architecture as not initialized.

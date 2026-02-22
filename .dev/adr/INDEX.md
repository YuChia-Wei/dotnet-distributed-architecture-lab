# .NET ADR Index

This index tracks the .NET ADR set in `.dev/adr/`. Each ADR from `.dev/adr/` must be **Copied** or **Translated** here unless explicitly **Discarded**.

Legend:
- **Translate** = adapt to .NET stack
- **Copy** = tech‑neutral ADR, preserved as‑is
- **Discard** = not applicable to .NET (explicitly listed)

## ADR Mapping Table

| ADR | Decision | Notes |
| --- | --- | --- |
| ADR-001-usecase-package-structure | Translate | Map packages to .NET namespaces |
| ADR-002-orm-config-location | Translate | EF Core config + DI |
| ADR-003-spring-config-structure | Translate | ASP.NET Core DI & Options Pattern |
| ADR-004-sub-agent-architecture-decision | Copy | Prompt system architecture |
| ADR-005-ai-task-execution-standard-operating-procedure | Copy | SOP |
| ADR-006-rest-api-path-design | Copy | REST design rules |
| ADR-007-task-file-format-standardization | Copy | Task file format |
| ADR-009-command-query-subagent-separation | Copy | Prompt decomposition |
| ADR-010-no-component-annotation-for-services | Translate | Explicit DI registration |
| ADR-012-task-moved-event-design | Copy | Domain event design |
| ADR-013-task-results-tracking | Copy | Task tracking policy |
| ADR-018-pbi-state-transition-invariant-handling | Translate | Convert Java examples to C# |
| ADR-019-outbox-pattern-implementation | Translate | WolverineFx + EF Core + PostgreSQL |
| ADR-020-archive-pattern-implementation | Translate | Query model CRUD |
| ADR-021-aggregate-field-initialization-pattern | Translate | C# aggregate init pattern |
| ADR-021-profile-based-testing-architecture | Translate | xUnit + env config |
| ADR-023-outbox-mapper-complete-entity-mapping-requirement | Translate | .NET serialization rules |
| ADR-024-test-isolation-and-domain-event-mapper | Translate | Test isolation + mapper rules |
| ADR-025-mutation-testing-ucontract-exclusion | Translate | Stryker.NET policy |
| ADR-027-sprint-meeting-fields-addition | Copy | Domain model change |
| ADR-028-unassigned-pbi-query-design | Copy | Query behavior |
| ADR-029-no-custom-repository-interfaces | Translate | Repository rule in .NET |
| ADR-031-reactor-interface-definition | Translate | WolverineFx reactor interface |
| ADR-034-task-completion-notification | Copy | Tooling/macOS (kept for completeness) |
| ADR-035-transaction-outbox-pattern | Translate | EF Core + outbox strategy |
| ADR-036-parallel-task-execution-strategy | Copy | Process/tooling |
| ADR-040-spring-profile-configuration-loading | Translate | appsettings.{Environment}.json |
| ADR-041-mapper-serialization-requirements | Translate | System.Text.Json config |
| ADR-042-deprecate-generic-code-generation-prompt | Copy | Prompt policy |
| ADR-042-script-generation-from-markdown-documentation | Copy | Tooling policy |
| ADR-043-audit-fields-in-event-metadata | Translate | Event metadata rules |
| ADR-044-profile-based-dependency-injection | Translate | DI policy |
| ADR-045-sub-agent-prompts-modularization | Copy | Prompt architecture |
| ADR-046-query-side-layering-strategy | Translate | Query Repository + Query Service layering |
| ADR-047-shared-project-classification | Translate | Shared projects classification and dependency rules |
| ADR-048-slnx-logical-solution-folder-structure | Translate | Adopt logical Solution Folder grouping with fixed slash style |
| ADR-049-dockerfile-explicit-csproj-copy-for-restore-cache | Translate | Keep explicit csproj COPY before restore for Docker layer cache, with script-based sync check |

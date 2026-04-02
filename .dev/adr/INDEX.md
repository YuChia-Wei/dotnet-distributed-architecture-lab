# .NET ADR Index

This index tracks the authoritative ADR set in `.dev/adr/`.

## Status Legend

| Status | Meaning |
| --- | --- |
| `Active ADR` | 仍然是主要決策入口，尚未完全被其他 canonical 文件吸收 |
| `Landed in Standards` | 規則已被正式標準 / guide / architecture file 承接 |
| `Historical / Superseded` | 保留決策脈絡，但已不是 active source of truth |

## ADR Index

| ADR | Focus | Status | Primary Canonical Source |
| --- | --- | --- | --- |
| ADR-001-usecase-package-structure | Use case package and namespace structure | Landed in Standards | `.dev/standards/project-structure.md` |
| ADR-002-orm-config-location | ORM configuration location | Active ADR | ADR itself |
| ADR-003-spring-config-structure | DI and configuration structure | Landed in Standards | `.dev/standards/ASPNET-CORE-CONFIGURATION-CHECKLIST.md` |
| ADR-004-sub-agent-architecture-decision | Sub-agent architecture decision | Historical / Superseded | `.ai/SUB-AGENT-SYSTEM.MD` |
| ADR-005-ai-task-execution-standard-operating-procedure | AI task execution SOP | Active ADR | ADR itself |
| ADR-006-rest-api-path-design | REST API path design | Landed in Standards | `.dev/standards/coding-standards/controller-standards.md` |
| ADR-007-task-file-format-standardization | Task file format | Historical / Superseded | `.dev/refactor-workflows/README.MD` |
| ADR-009-command-query-subagent-separation | Command/query sub-agent separation | Landed in Standards | `.ai/SUB-AGENT-SYSTEM.MD` |
| ADR-010-no-component-annotation-for-services | Explicit service registration | Landed in Standards | `.dev/guides/implementation-guides/DOTNET-DI-TEST-GUIDE.md` |
| ADR-012-task-moved-event-design | Task moved event design | Active ADR | ADR itself |
| ADR-013-task-results-tracking | Task results tracking | Historical / Superseded | `.dev/refactor-workflows/README.MD` |
| ADR-018-pbi-state-transition-invariant-handling | State transition invariant handling | Active ADR | ADR itself |
| ADR-019-outbox-pattern-implementation | Outbox pattern implementation | Landed in Standards | `.dev/standards/coding-standards.md` |
| ADR-020-archive-pattern-implementation | Archive/query model implementation | Landed in Standards | `.dev/standards/coding-standards/archive-standards.md` |
| ADR-021-aggregate-field-initialization-pattern | Aggregate field initialization pattern | Landed in Standards | `.dev/standards/coding-standards/aggregate-standards.md` |
| ADR-023-outbox-mapper-complete-entity-mapping-requirement | Outbox mapper completeness requirement | Landed in Standards | `.dev/guides/design-guides/FRAMEWORK-API-INTEGRATION-GUIDE.md` |
| ADR-024-test-isolation-and-domain-event-mapper | Test isolation and domain event mapper | Active ADR | ADR itself |
| ADR-025-mutation-testing-ucontract-exclusion | Mutation testing exclusion policy | Landed in Standards | `.dev/standards/coding-standards.md` |
| ADR-027-sprint-meeting-fields-addition | Sprint meeting field addition | Historical / Superseded | project-specific feature history |
| ADR-028-unassigned-pbi-query-design | Unassigned PBI query design | Historical / Superseded | project-specific feature history |
| ADR-029-no-custom-repository-interfaces | No custom repository interfaces | Landed in Standards | `.dev/standards/coding-standards.md` |
| ADR-031-reactor-interface-definition | Reactor interface definition | Landed in Standards | `.dev/standards/coding-standards/reactor-standards.md` |
| ADR-034-task-completion-notification | Task completion notification | Historical / Superseded | workflow/tooling history |
| ADR-035-transaction-outbox-pattern | Transaction outbox pattern | Landed in Standards | `.dev/standards/coding-standards.md` |
| ADR-036-parallel-task-execution-strategy | Parallel task execution strategy | Historical / Superseded | workflow/tooling history |
| ADR-040-spring-profile-configuration-loading | Profile/environment configuration loading | Landed in Standards | `.dev/standards/ASPNET-CORE-CONFIGURATION-CHECKLIST.md` |
| ADR-041-mapper-serialization-requirements | Mapper serialization requirements | Landed in Standards | `.dev/standards/coding-standards/mapper-standards.md` |
| ADR-042-deprecate-generic-code-generation-prompt | Prompt deprecation policy | Historical / Superseded | `.ai/SUB-AGENT-SYSTEM.MD` |
| ADR-043-audit-fields-in-event-metadata | Audit fields in event metadata | Landed in Standards | `AGENTS.md` |
| ADR-044-profile-based-dependency-injection | Profile-based dependency injection | Landed in Standards | `.dev/guides/implementation-guides/PROFILE-CONFIGURATION-COMPLEXITY-SOLUTION.md` |
| ADR-045-sub-agent-prompts-modularization | Sub-agent prompt modularization | Landed in Standards | `.ai/SUB-AGENT-SYSTEM.MD` |
| ADR-046-query-side-layering-strategy | Query-side layering strategy | Landed in Standards | `.dev/standards/coding-standards.md` |
| ADR-047-shared-project-classification | Shared project classification | Landed in Standards | `.dev/standards/project-structure.md` |
| ADR-048-slnx-logical-solution-folder-structure | Solution folder structure | Landed in Standards | `.dev/standards/project-structure.md` |
| ADR-049-dockerfile-explicit-csproj-copy-for-restore-cache | Docker restore-cache csproj copy rule | Active ADR | ADR itself |
| ADR-050-skill-and-sub-agent-boundary | Skill and sub-agent boundary | Landed in Standards | `.ai/SUB-AGENT-SYSTEM.MD` |
| ADR-051-profile-based-testing-architecture | Profile-based testing architecture | Landed in Standards | `.dev/guides/design-guides/PROFILE-BASED-TESTING-GUIDE.md` |
| ADR-052-script-generation-from-markdown-documentation | Script generation from markdown documentation | Landed in Standards | `.ai/scripts/MD-SCRIPT-GENERATION-GUIDE.md` |

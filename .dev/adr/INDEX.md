# .NET ADR Index

This index tracks the authoritative ADR set in `.dev/adr/`.

## Status Legend

| Status | Meaning |
| --- | --- |
| `Active ADR` | 仍然是主要決策入口，尚未完全被其他 canonical 文件吸收 |
| `Landed in Standards` | 規則已被正式標準 / guide / architecture file 承接 |
| `Historical / Superseded` | 保留決策脈絡，但已不是 active source of truth |
| `Historical / Project-Specific` | 主要屬於舊產品或單一 bounded context 的歷史設計，不作為跨專案知識入口 |

## ADR Index

| ADR | Focus | Status | Primary Canonical Source |
| --- | --- | --- | --- |
| ADR-001-usecase-package-structure | Use case package and namespace structure | Landed in Standards | `.dev/standards/project-structure.md` |
| ADR-002-orm-config-location | ORM configuration location | Landed in Standards | `.dev/guides/implementation-guides/PERSISTENCE-CONFIGURATION-GUIDE.md` |
| ADR-003-spring-config-structure | DI and configuration structure | Landed in Standards | `.dev/standards/ASPNET-CORE-CONFIGURATION-CHECKLIST.md` |
| ADR-004-sub-agent-architecture-decision | Sub-agent architecture decision | Historical / Superseded | `.ai/SUB-AGENT-SYSTEM.MD` |
| ADR-005-ai-task-execution-standard-operating-procedure | AI task execution SOP | Landed in Standards | `.dev/guides/ai-collaboration-guides/AI-COLLABORATION-WORKFLOW-GUIDE.md` |
| ADR-007-task-file-format-standardization | Task file format | Historical / Superseded | `.dev/refactor-workflows/README.MD` |
| ADR-009-command-query-subagent-separation | Command/query sub-agent separation | Landed in Standards | `.ai/SUB-AGENT-SYSTEM.MD` |
| ADR-010-no-component-annotation-for-services | Explicit service registration | Landed in Standards | `.dev/guides/implementation-guides/DOTNET-DI-TEST-GUIDE.md` |
| ADR-012-task-moved-event-design | Task moved event design | Historical / Project-Specific | project-specific domain history |
| ADR-013-task-results-tracking | Task results tracking | Historical / Superseded | `.dev/refactor-workflows/README.MD` |
| ADR-018-pbi-state-transition-invariant-handling | State transition invariant handling | Historical / Project-Specific | project-specific domain history |
| ADR-019-outbox-pattern-implementation | Outbox pattern implementation | Landed in Standards | `.dev/standards/coding-standards.md` |
| ADR-020-archive-pattern-implementation | Archive/query model implementation | Landed in Standards | `.dev/standards/coding-standards/archive-standards.md` |
| ADR-021-aggregate-field-initialization-pattern | Aggregate field initialization pattern | Landed in Standards | `.dev/standards/coding-standards/aggregate-standards.md` |
| ADR-023-outbox-mapper-complete-entity-mapping-requirement | Outbox mapper completeness requirement | Landed in Standards | `.dev/guides/design-guides/FRAMEWORK-API-INTEGRATION-GUIDE.md` |
| ADR-024-test-isolation-and-domain-event-mapper | Test isolation and domain event mapper | Landed in Standards | `.dev/standards/coding-standards/test-standards.md` |
| ADR-025-mutation-testing-ucontract-exclusion | Mutation testing exclusion policy | Landed in Standards | `.dev/standards/coding-standards.md` |
| ADR-027-sprint-meeting-fields-addition | Sprint meeting field addition | Historical / Project-Specific | project-specific feature history |
| ADR-028-unassigned-pbi-query-design | Unassigned PBI query design | Historical / Project-Specific | project-specific feature history |
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
| ADR-047-shared-project-classification | Shared project classification | Landed in Standards | `.dev/standards/project-structure.md` |
| ADR-048-slnx-logical-solution-folder-structure | Solution folder structure | Landed in Standards | `.dev/standards/project-structure.md` |
| ADR-049-dockerfile-explicit-csproj-copy-for-restore-cache | Docker restore-cache csproj copy rule | Landed in Standards | `.dev/guides/implementation-guides/DOCKER-RESTORE-CACHE-GUIDE.md` |
| ADR-050-skill-and-sub-agent-boundary | Skill and sub-agent boundary | Historical / Superseded | `.dev/guides/ai-collaboration-guides/SKILL-AND-SUB-AGENT-TAXONOMY-GUIDE.md` |
| ADR-052-script-generation-from-markdown-documentation | Script generation from markdown documentation | Landed in Standards | `.ai/scripts/MD-SCRIPT-GENERATION-GUIDE.md` |

# AGENTS.md

## Scope & Precedence

- This document serves as the collaboration guideline for AI agents and humans across the entire repository.
- If a subdirectory has another AGENTS.* file, the deeper one takes precedence.
- Command priority: User/Approval > Subfolder AGENTS > This file > Other general documents.
- 若有設定 IDE 的 MCP Server 則優先使用 IDE MCP Server 中有提供的重構功能。

## Quick Start for AI Agents

1. Read `.dev/ARCHITECTURE.MD` and `.dev/requirement/TECH-STACK-REQUIREMENTS.MD`.
2. Use `.dev/adr/README.md` and `.dev/adr/INDEX.md` as the single source of ADR truth.
3. For reusable AI-specific prompts, use `.ai/` folder.
4. When preparing this framework for reuse in another repo, follow `.dev/PORTABLE-PACKAGING-GUIDE.MD`.

---

## Mandatory Workflows

### Code Review (Required)

1. Read `.ai/CODE-REVIEW-INDEX.MD`.
2. Read `.claude/skills/code-reviewer/CHECKLIST-REFERENCE.MD` for detailed rules.
3. Identify file type and read the matching section in `.dev/standards/CODE-REVIEW-CHECKLIST.md`.
4. Build a checklist comparison table.
5. Categorize issues (CRITICAL / MUST FIX / SHOULD FIX).
6. If tests apply, run `dotnet test --filter FullyQualifiedName~[TestClassName]`.

### Spec Compliance (Required for Problem Frames)

When using problem-frame workflows:
1. Run `dotnet/spec-compliance-validator` skill.
2. **Gate**: coverage must be 100%. If not, return to implementation/test generation.

### Task Execution (If task-*.json is used)

1. Read task JSON.
2. Implement.
3. Run tests (if required).
4. Update `status` + `results` in task JSON.

Workflow artifact location:
- Use `.dev/refactor-workflows/<workflow-id>/refactor-plan.md`
- Use `.dev/refactor-workflows/<workflow-id>/review-report.md`
- Use `.dev/refactor-workflows/<workflow-id>/tasks/<task-id>.json`
- Do not scatter workflow artifacts under `.ai/`, `.claude/skills/`, or arbitrary feature folders unless the user explicitly requests it.

### Portable Packaging (When framework files are copied to another repo)

1. Keep framework-level guides, standards, scripts, and collaboration rules.
2. Remove or rewrite project-specific requirement, spec, operations, workflow, and ADR truth.
3. Rebuild `.dev/requirement/`, `.dev/specs/`, `.dev/operations/`, and `ADR-*.md` from the target project's facts.
4. Treat `.dev/PORTABLE-PACKAGING-GUIDE.MD` as the authoritative migration boundary.

---

## Sub-agent System Overview

- Primary reference: `.ai/SUB-AGENT-SYSTEM.MD`
- Use `.ai/assets/sub-agent-role-prompts/` for canonical delegated sub-agent definitions.
- Use `.ai/assets/shared/` for shared rules, examples, and supporting materials.
- Use `.ai/scripts/` for .NET code generation scripts.

---

## .NET Stack Rules

| Category | Rule |
| :--- | :--- |
| **Stack** | .NET 10 (C# 14), Dapper + EF Core (mixed), WolverineFx 5.16.2, xUnit 2.9.3, NSubstitute, PostgreSQL 16, RabbitMQ + Kafka |
| **ORM Strategy** | Write: Dapper + Npgsql; Read/Projection: EF Core or Dapper |
| **Testing** | xUnit (BDDfy planned for future); **no BaseTestClass** |
| **DI** | Use `IServiceCollection`; no attribute-based scanning |
| **Repository** | Generic `IRepository<T, TId>` only; no custom interfaces; queries via QueryService/Projection |
| **Audit fields** | Stored in Domain Event metadata (ADR-043) |
| **Config** | `appsettings.{Environment}.json` + `DOTNET_ENVIRONMENT` |
| **Shared interfaces** | Use `BuildingBlocks.*` namespaces |
| **Cross-BC Communication** | **Must use MQ only** (RabbitMQ/Kafka); Web API is forbidden |

---

## Skill Index (.claude/skills/)

| Skill | Purpose | Trigger | Status |
| :--- | :--- | :--- | :--- |
| `code-reviewer` | .NET code review workflow | "code review" | ✅ Active |
| `spec-compliance-validator` | Spec 100% gate for .NET | "validate spec" | ✅ Active |
| `ddd-ca-hex-architect` | Repo architecture design workflow for DDD + CA + HEX + MQ | "architect", "DDD", "CA", "Hexagonal", "HEX" | ✅ Active |
| `bdd-gwt-test-designer` | Given-When-Then test design workflow from requirements, specs, or existing behavior | "BDD", "Gherkin", "Given-When-Then", "test design" | ✅ Active |
| `staged-refactor-implementer` | Incremental refactor execution workflow from plans and findings | "refactor", "implement stage", "execute refactor plan" | ✅ Active |
| `tactical-refactor-implementer` | Local structural refactor workflow around one main target | "extract method", "local rename", "safe rename", "small local cleanup" | ✅ Active |

---

## File & Directory Index

### AI-Specific (`.ai/`)

| Path | Description |
| :--- | :--- |
| `.ai/INDEX.MD` | AI 文件入口 |
| `.ai/README.MD` | .NET Framework 概覽 |
| `.ai/CODE-REVIEW-INDEX.MD` | Code Review 索引 |
| `.ai/SUB-AGENT-SYSTEM.MD` | Sub-agent 系統說明 |
| `.ai/BUILDING-BLOCKS-CLASS-INDEX.MD` | 共用介面索引 |
| `.ai/assets/` | Portable canonical AI assets |
| `.ai/scripts/` | .NET code generation scripts |

### Project Knowledge (`.dev/`)

| Path | Description |
| :--- | :--- |
| `.dev/ARCHITECTURE.MD` | 系統架構 |
| `.dev/README.MD` | 專案知識入口 |
| `.dev/adr/` | 架構決策紀錄 (ADR) |
| `.dev/guides/` | 學習指南 |
| `.dev/lessons/` | 經驗教訓 |
| `.dev/requirement/` | 技術需求 |
| `.dev/refactor-workflows/` | 跨 skill / subagent workflow artifacts（plan / review-report / task） |
| `.dev/specs/` | 功能規格與行為規格 |
| `.dev/standards/` | Code Review Checklist, Project Structure |

### Claude Skills (`.claude/skills/`)

| Path | Description |
| :--- | :--- |
| `.claude/skills/README.md` | Claude skills 入口與 skill index |
| `.claude/skills/code-reviewer/` | Code Review Skill + CHECKLIST-REFERENCE.MD |
| `.claude/skills/spec-compliance-validator/` | Spec Compliance Skill |
| `.claude/skills/ddd-ca-hex-architect/` | Architecture design skill for DDD + CA + HEX + MQ-first decisions |
| `.claude/skills/bdd-gwt-test-designer/` | BDD / Gherkin Given-When-Then test design skill |
| `.claude/skills/staged-refactor-implementer/` | Incremental refactor implementation skill for staged execution |
| `.claude/skills/tactical-refactor-implementer/` | Local object-centered refactor implementation skill |

### AI Collaboration Guides (`.dev/guides/ai-collaboration-guides/`)

| Path | Description |
| :--- | :--- |
| `.dev/guides/ai-collaboration-guides/README.MD` | AI collaboration guides 入口 |
| `.dev/guides/ai-collaboration-guides/LOCAL-RUNTIME-WRAPPER-GUIDE.md` | Repo wrapper 與本機 runtime 的使用說明 |
| `.dev/guides/ai-collaboration-guides/DDD-CA-HEX-ARCHITECT-SKILL-GUIDE.md` | Human-facing guide and prompt templates for invoking the architect skill |
| `.dev/guides/ai-collaboration-guides/BDD-GWT-TEST-DESIGNER-SKILL-GUIDE.md` | Human-facing guide and prompt templates for invoking the BDD GWT test designer skill |
| `.dev/guides/ai-collaboration-guides/STAGED-REFACTOR-IMPLEMENTER-SKILL-GUIDE.md` | Human-facing guide and prompt templates for invoking the refactor implementation skill |
| `.dev/guides/ai-collaboration-guides/TACTICAL-REFACTOR-IMPLEMENTER-SKILL-GUIDE.md` | Human-facing guide and prompt templates for invoking the tactical refactor skill |
| `.codex/skills/README.md` | Codex runtime skill wrapper 入口 |
| `.gemini/commands/README.md` | Gemini wrapper command 入口 |
| `.github/prompts/README.md` | GitHub Copilot wrapper prompt 入口 |
| `.github/copilot-instructions.md` | GitHub Copilot repo-level instructions |


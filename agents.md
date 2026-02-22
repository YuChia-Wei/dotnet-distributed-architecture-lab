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

---

## Mandatory Workflows

### Code Review (Required)

1. Read `.ai/CODE-REVIEW-INDEX.MD`.
2. Read `.claude/skills//code-reviewer/CHECKLIST-REFERENCE.MD` for detailed rules.
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

---

## Sub-agent System Overview

- Primary reference: `.ai/SUB-AGENT-SYSTEM.MD`
- Use `.ai/prompts/` for .NET sub-agent workflows.
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
| `.ai/prompts/` | .NET sub-agent prompts |
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
| `.dev/standards/` | Code Review Checklist, Project Structure |

### Claude Skills (`.claude/skills/`)

| Path | Description |
| :--- | :--- |
| `.claude/skills/code-reviewer/` | Code Review Skill + CHECKLIST-REFERENCE.MD |
| `.claude/skills/spec-compliance-validator/` | Spec Compliance Skill |

# ADR Consolidation First Pass

本文件記錄 `.dev/adr/` 的第一輪整理結果，目的是找出：

- 哪些 ADR 的規則已經落地成正式標準文件
- 哪些 ADR 只有部分被吸收，仍需要補 canonical file
- 哪些 ADR 比較像歷史事件或專案特例，不適合再當成跨專案標準

## 判斷原則

- 若規則已被 `.dev/standards/`、`.dev/specs/`、`.dev/operations/`、`.dev/guides/` 或 `.ai/` 的 canonical 文件正式承接，視為「已落地」
- 若只有零散提到、沒有單一標準文件承接，視為「部分落地」
- 若內容主要描述單一功能、單一歷史事件、或已被後續流程取代，視為「歷史 / 特例」

## 1. 已落地成標準或架構文件

| ADR | 主題 | 已承接文件 |
| --- | --- | --- |
| ADR-001 | Use case package / namespace structure | `standards/project-structure.md`, `standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD`, `ARCHITECTURE.MD` |
| ADR-003 | DI / configuration structure | `standards/ASPNET-CORE-CONFIGURATION-CHECKLIST.md`, `guides/implementation-guides/PROFILE-CONFIGURATION-COMPLEXITY-SOLUTION.md`, `DOTNET-DI-TEST-GUIDE.md` |
| ADR-006 | REST API path design | `standards/coding-standards/controller-standards.md` |
| ADR-009 | Command / Query / Reactor separation | `.ai/SUB-AGENT-SYSTEM.MD`, `guides/ai-collaboration-guides/DDD-CA-HEX-ARCHITECT-SKILL-GUIDE.md`, `standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD` |
| ADR-010 | Explicit service registration / no annotation scanning | `AGENTS.md`, `guides/implementation-guides/DOTNET-DI-TEST-GUIDE.md`, `standards/coding-standards/*` 中的 `IServiceCollection` 規範 |
| ADR-019 | Outbox pattern implementation | `ARCHITECTURE.MD`, `requirement/TECH-STACK-REQUIREMENTS.MD`, `standards/coding-standards.md`, `operations/mq-topology.md`, `guides/design-guides/FRAMEWORK-API-INTEGRATION-GUIDE.md` |
| ADR-020 | Archive pattern implementation | `standards/coding-standards/archive-standards.md` |
| ADR-021 | Aggregate field initialization pattern | `standards/coding-standards/aggregate-standards.md`, `standards/CODE-REVIEW-CHECKLIST.md` |
| ADR-023 | Outbox mapper complete entity mapping | `guides/design-guides/FRAMEWORK-API-INTEGRATION-GUIDE.md`, `standards/coding-standards/aggregate-standards.md` |
| ADR-025 | Mutation testing exclusion policy | `requirement/TECH-STACK-REQUIREMENTS.MD`, `standards/coding-standards.md` |
| ADR-029 | No custom repository interfaces | `standards/coding-standards.md`, `standards/anti-patterns.md`, `standards/CODE-REVIEW-CHECKLIST.md`, `BUILDING-BLOCKS-CLASS-INDEX.MD` |
| ADR-035 | Transaction outbox pattern | 同 ADR-019 的承接文件；目前可視為已被 Outbox 基準吸收 |
| ADR-040 | Environment / profile configuration loading | `standards/ASPNET-CORE-CONFIGURATION-CHECKLIST.md`, `guides/implementation-guides/PROFILE-CONFIGURATION-COMPLEXITY-SOLUTION.md` |
| ADR-043 | Audit fields in event metadata | `AGENTS.md` 的 stack rules、相關 aggregate / event 設計規則 |
| ADR-044 | Profile-based dependency injection | `guides/implementation-guides/PROFILE-CONFIGURATION-COMPLEXITY-SOLUTION.md`, `ASPNET-CORE-CONFIGURATION-CHECKLIST.md` |
| ADR-045 | Sub-agent prompt modularization | `.ai/SUB-AGENT-SYSTEM.MD`, `guides/ai-collaboration-guides/AI-ASSET-LOCATION-STRATEGY.md` |
| ADR-046 | Query-side layering strategy | `standards/coding-standards.md`, `standards/project-structure.md`, `standards/CODE-REVIEW-CHECKLIST.md` |
| ADR-047 | Shared project classification | `standards/project-structure.md` |
| ADR-048 | `.slnx` logical solution folder structure | `standards/project-structure.md` |
| ADR-050 | Skill and sub-agent boundary | `.ai/SUB-AGENT-SYSTEM.MD`, `guides/ai-collaboration-guides/AI-REFACTORING-SKILL-BOUNDARY-GUIDE.md` |
| ADR-051 | Profile-based testing architecture | `requirement/TECH-STACK-REQUIREMENTS.MD`, `guides/design-guides/PROFILE-BASED-TESTING-GUIDE.md`, `standards/coding-standards.md` |
| ADR-052 | Script generation from markdown documentation | `.ai/scripts/README.md`, `.ai/scripts/MD-SCRIPT-GENERATION-GUIDE.md` |

## 2. 部分落地，但仍缺正式承接文件

| ADR | 主題 | 目前狀態 | 建議 |
| --- | --- | --- | --- |
| ADR-002 | EF Core configuration location | 有技術棧與結構描述，但缺一份專門的 ORM / EF Core config standard | 考慮補到 `standards/` 或 `guides/design-guides/` |
| ADR-004 | Sub-agent architecture decision | 大方向已被 `.ai/SUB-AGENT-SYSTEM.MD` 吸收，但內文仍含大量歷史 prompt-first 脈絡 | 之後可轉成 superseded / historical ADR |
| ADR-005 | AI task execution SOP | 現在有 `AI-COLLABORATION-WORKFLOW-GUIDE.md` 與 `refactor-workflows/README.MD`，但沒有完整吸收 SOP 細則 | 需決定是否補成 workflow standard，或將 ADR 標成 historical |
| ADR-007 | Task file format standardization | 舊 `.dev/tasks/*` 模型與現在的 `.dev/refactor-workflows/` artifact contract 已不一致 | 高優先檢查是否應廢止或重寫 |
| ADR-024 | Test isolation and domain event mapper | 測試與 outbox 規則已分散在 testing / framework guides，但未集中承接 | 可考慮補到 `test-standards.md` 或 `FRAMEWORK-API-INTEGRATION-GUIDE.md` |
| ADR-031 | Reactor interface uses `DomainEventData` | 仍主要停留在 ADR；目前缺一份 reactor-specific standard 明寫這條規則 | 若 repo 仍使用此模式，應補正式標準文件 |
| ADR-041 | Mapper serialization requirements | 有 Framework API integration 與 data class 規則，但缺 mapper serialization 的 canonical standard | 可補到 `mapper-standards.md` |
| ADR-049 | Dockerfile explicit csproj copy | 目前較像 build/deployment rule，尚未看到專門的 deployment / docker standard | 可補 `guides/implementation-guides/` 或 `standards/` |

## 3. 較像歷史事件、單一功能、或專案特例

這些 ADR 目前看起來不適合直接升格為跨專案標準：

| ADR | 原因 |
| --- | --- |
| ADR-012 | 單一 TaskMoved event 設計，偏特定 domain / feature |
| ADR-013 | task results tracking，已有新 workflow artifact contract，需判斷是否只保留歷史脈絡 |
| ADR-018 | PBI state transition invariant handling，偏單一 aggregate / feature |
| ADR-027 | Sprint meeting fields addition，單一功能變更 |
| ADR-028 | Unassigned PBI query design，單一查詢設計 |
| ADR-034 | task completion notification，偏工作方式 / 工具互動，不是目前 repo 的核心 architecture standard |
| ADR-036 | parallel task execution strategy，偏當時 sub-agent workflow 效率議題 |
| ADR-042 | deprecate generic code generation prompt，已偏歷史 prompt 資產遷移事件 |

## 4. 第一輪整理結論

### 已可判定為「規則已落地」的主軸

- application / use case / handler 關係
- controller 邊界
- repository 限制
- query-side layering
- outbox / archive / profile-based testing
- skill / sub-agent / workflow 邊界
- shared project classification
- solution folder structure

### 目前最值得優先處理的 ADR

1. `ADR-007-task-file-format-standardization`
   - 舊 task model 與現行 `refactor-workflows` contract 明顯不一致
2. `ADR-031-reactor-interface-definition`
   - 若仍是 active rule，應移到正式 standard
3. `ADR-041-mapper-serialization-requirements`
   - 有 active value，但還沒正式落到 mapper standard
4. `ADR-004` / `ADR-042`
   - 屬於 prompt-first 時代遺留，應重新判斷是否保留為歷史 ADR

## 5. 下一步建議

第二輪可直接依這份盤點做三件事：

1. 在 `INDEX.md` 補狀態欄位：
   - `Active ADR`
   - `Landed in standards`
   - `Historical / superseded`
2. 為 `ADR-031`、`ADR-041`、`ADR-049` 補正式承接文件
3. 對 `ADR-007`、`ADR-013`、`ADR-034`、`ADR-036`、`ADR-042` 做清理決策

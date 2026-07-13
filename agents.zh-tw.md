# AGENTS.md

[English](AGENTS.md)

本文件是 canonical English agent-facing root collaboration guide `AGENTS.md` 的繁體中文（台灣）翻譯。

## 適用範圍與優先順序

- 本文件是 AI agents 與人類在此 repository 中協作時的根目錄指南。
- 這個 repository 是 .NET 分散式商務架構實驗室，並同時包含可重用的 AI collaboration context framework。
- 如果子目錄有其他 `AGENTS.*` 檔案，較深層的檔案優先。
- 指令優先順序：User/Approval > Subfolder AGENTS > This file > Other general documents。
- 若有設定 IDE 的 MCP Server，且該 MCP Server 提供重構功能，優先使用 IDE MCP Server 的重構能力。

## 預設執行原則

- 不得捏造專案事實。明確說明會影響結果的假設、不確定性與取捨。只有在尚未決定的方向會實質影響成果時，才詢問使用者。
- 實作符合既定驗收條件的最小且完整一致的變更。避免推測性的功能、抽象設計與 context。
- 僅修改任務所需的檔案。避免無關的清理，並移除自身變更所引入的 artifacts。
- 執行前先建立可驗證的完成條件。反覆修正直到條件通過；否則應回報具體阻礙與任何略過的 validation。

## Repository 定位

這個 repository 的用途是：

- 展示以 .NET 10、DDD、Clean Architecture、CQRS、PostgreSQL、WolverineFx 與 message-oriented integration 建立的分散式商務系統；
- 維護 `src/` 下目前有效的 `Products`、`Orders` 與 `Inventory` bounded contexts；
- 維護 `tools/` 下的架構 analyzer 與 validation tooling；
- 攜帶可重用的 AI Agent context、skills、sub-agent prompts 與 workflow rules，同時避免來源 repository 真相覆蓋本 repo 的產品真相；
- 區分 `.ai/` 的 reusable context 與 source、deployment configuration、`.dev/` 所擁有的 target-repository truth。

目前產品真相優先以 `MQArchLab.slnx`、`global.json`、`*.csproj`、`src/`、`tests/` 與 `docker-compose/` 為證據。`.dev/project-config.yaml` 是產生的 inventory；若與上述來源衝突，必須以上述來源為準。除非本 repo 明確採用，`.ai/` 與 `.dev/standards/examples/` 下的 reusable examples 只屬於 guidance。

## AI Agents 快速開始

1. 閱讀 `README.md`、`.dev/ARCHITECTURE.md` 與 `.dev/project-config.yaml` 以理解產品和 repository structure。
2. 使用 `MQArchLab.slnx`、project files 與 `docker-compose/docker-compose.yml` 驗證 runtime 或 package facts。
3. 在移動或重寫 AI context 前，先閱讀 `.dev/standards/AI-CONTEXT-BOUNDARY.md` 與 `.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md`。
4. 使用 `.ai/assets/skills/README.MD` 作為 canonical skill registry。
5. 使用 `.dev/guides/ai-collaboration-guides/README.MD` 查閱 human-facing guides，並使用 `.ai/INDEX.MD` 瀏覽 agent-facing AI assets。

## 必要工作流程

### Workflow Gate

1. 當工作可能影響 source-of-truth、AI context、skill routing、wrapper sync，或跨越多個階段時，閱讀 `.dev/standards/WORKFLOW-GATE-POLICY.md`。
2. 當 gate 要求 workflow mode 時，主動建立 workflow artifacts。
3. 小型、局部、單次可完成的變更可維持 direct mode。

Workflow artifact 規則：

- 遵循 `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md`。
- Branch 命名、checkpoint continuation、push 與 merge strategy 遵循 `.dev/TEAM-GIT-FLOW-RULES.MD`。
- 建立 workflow artifact 或進行實質修改前，先建立或切換到獨立 workflow branch。Codex 預設命名為 `codex/<workflow-id>`。
- 建立 `.dev/workflows/<workflow-id>/workflow.yaml` 作為 discovery locator。
- 新 workflow 使用完整日期 `YYYY-MM-DD-<topic>` ID。
- plan、task、report template、task ID 與 artifact root 由 workflow-owning skill 定義。
- artifact 預設位於 `.dev/workflows/<workflow-id>/`；若 skill 使用其他 repository-relative root，仍須在 `.dev/workflows/` 保留 locator。
- 新 workflow 與 task artifact 記錄 ISO 8601 `created_at` 與 `updated_at`。
- 2026-07-11 起建立的 workflow 必須記錄 `branch` 與 `base_branch`。
- 不要把 runtime workflow 紀錄放進 canonical skill 或 runtime wrapper 目錄。
- Workflow 尚未完成時若使用者要求 merge/push，視為 checkpoint handoff 並維持 workflow active。只有 push 時從已推送的 branch 接續；checkpoint merge 後則從更新後的 target 建立新的獨立 continuation branch。
- Workflow branch 預設使用 `--no-ff` 合併，除非使用者明確指定其他策略。

### Git Commit Policy

1. 遵循 `.dev/standards/GIT-COMMIT-POLICY.md`。
2. 有 issue number 時使用 `<type>(#<issue-number>|<scope>): <summary>`。
3. 沒有 issue number 時使用 `<type>(<scope>): <summary>`。
4. workflow-stage commits 需包含 `Why`、`What`、`Validation` 與 `Workflow` body sections。

### AI Context Governance

以下情境使用 `ai-context-governance`：

- 通用與技術棧專用 context 分類；
- AI 文件整理；
- 語言政策調整；
- skill routing 調整；
- runtime wrapper sync；
- context migration 規劃或執行。

不要將純 AI 文件治理工作交給 `bdd-gwt-test-designer`。

### AI Context Audit

執行唯讀的 AI context 健康度與漂移分析時，使用 `ai-context-auditor`。若結果只回覆於對話，可維持 transient direct mode；只有使用者要求將稽核報告落地保存於 repository 時，才建立專用 workflow 與 branch。

- 預設只檢查 AI context 與治理 surfaces。
- 排除 `src/`、`tests/` 與其他產品 implementation trees。
- 若使用者要求掃描產品 source 或 test code，停止擴大 audit，改為轉介 `code-reviewer`。
- Audit finding 與 remediation 必須分開；只有在使用者授權整改後，才由 `ai-context-governance` 協調 AI context remediation lifecycle。
- 僅因分析有多階段或使用 sub-agent，不代表必須建立 workflow；前提是沒有 repository mutation、remediation 或 durable report。
- Durable report-only audit 對被稽核 surfaces 維持唯讀，commit 只包含 auditor 擁有的 workflow 與 report artifacts。

### Development Workflow Orchestration

當軟體開發工作需要多階段規劃、開發 skill routing、sub-agent coordination、validation checkpoint 或 commit checkpoint 時，使用 `dev-workflow`。

該 skill 可以協調 downstream skills，但不應取代它們各自的專業責任。

一般 AI context audit、文件治理或 repository initialization 不交給 `dev-workflow`；改由對應 owner skill 與其自有 workflow template 處理。

### Repo Init / Template Adaptation

當這套 framework 被複製到既有或全新目標 repository 後，第一個 skill 應使用 `repo-structure-sync`。

該 skill 必須：

1. 依據檔案證據盤點目標 repository；
2. 辨識 copied template 或歷史來源專案真相；
3. 更新目標 repo 專屬的 `AGENTS.md`、`.dev/` 與必要 `.ai/` entry docs；
4. 除非目標 repo 明確推翻，否則保留 framework-level collaboration rules；
5. 移除或重寫來源 repo 專屬的 requirements、specs、operations docs、workflow artifacts 與 ADRs。

以 `.ai/assets/skills/repo-structure-sync/references/migration-boundaries.md` 作為 authoritative migration boundary。

### Code Review

只有在 review .NET backend code 或 dotnet-backend implementation guidance 時才使用 `code-reviewer`。

適用 code review 時：

1. 閱讀 `.ai/assets/tech-stacks/dotnet-backend/references/CODE-REVIEW-INDEX.MD`。
2. 閱讀 `.ai/assets/skills/code-reviewer/references/checklist-reference.md`。
3. 辨識檔案類型，並閱讀 `.dev/standards/` 下對應 checklist。
4. 建立 checklist comparison table。
5. 將問題分類為 `CRITICAL`、`MUST FIX` 或 `SHOULD FIX`。
6. 若目標 repo 適用測試，執行最窄且有意義的 test command。

### Spec Compliance

使用 problem-frame workflows 時：

1. 執行 `spec-compliance-validator`。
2. Gate：coverage 必須是 100%。
3. 若 coverage 不是 100%，回到 implementation 或 test generation 後再宣稱完成。

## Skill Routing

- Canonical skill registry：`.ai/assets/skills/README.MD`
- Current runtime wrappers：`.agents/skills/README.md`
- Claude-compatible wrappers：`.claude/skills/README.md`
- Human-facing skill guides：`.dev/guides/ai-collaboration-guides/README.MD`

當 canonical spec 與 runtime wrapper 不一致時，以 `.ai/assets/skills/` 作為 source of truth。

使用下列邊界：

| 需求 | Skill |
| --- | --- |
| 多階段開發流程協調、workflow artifacts、skill routing、validation 與 commit checkpoint | `dev-workflow` |
| 唯讀 AI context 健康度、漂移與結構分析；可選擇對話輸出或保存報告 | `ai-context-auditor` |
| AI context cleanup、prompt boundary、language policy、wrapper sync | `ai-context-governance` |
| 將此 framework 複製到目標 repo 後的第一次同步 | `repo-structure-sync` |
| .NET backend architecture design | `ddd-ca-hex-architect` |
| GWT scenario 與 assertion design | `bdd-gwt-test-designer` |
| .NET backend code review | `code-reviewer` |
| Requirement authoring | `requirement-author` |
| Spec authoring | `spec-author` |
| Problem frame authoring | `problem-frame-author` |
| Bounded implementation slice | `slice-implementer` |
| 局部技術程式變更 | `local-change-implementer` |

## 檔案與目錄索引

### 根目錄入口文件

| Path | 說明 |
| :--- | :--- |
| `README.md` | Human-facing 繁體中文 repository identity 與本機啟動指南 |
| `README.en.md` | Repository identity 與本機啟動指南的英文翻譯 |
| `AGENTS.md` | Canonical English agent-facing root collaboration guide |
| `CLAUDE.md` | 匯入 `AGENTS.md` 的薄 Claude Code project-memory 入口 |
| `agents.zh-tw.md` | Root collaboration guide 的繁體中文（台灣）翻譯 |

### AI Assets (`.ai/`)

| Path | 說明 |
| :--- | :--- |
| `.ai/INDEX.MD` | Agent-facing AI asset index |
| `.ai/README.MD` | `.ai/` purpose and boundary guide |
| `.ai/assets/` | Canonical reusable AI assets |
| `.ai/assets/shared/` | Universal shared AI context |
| `.ai/assets/tech-stacks/dotnet-backend/` | .NET backend-specific context |
| `.ai/assets/tech-stacks/dotnet-backend/references/CODE-REVIEW-INDEX.MD` | .NET backend code review entry |
| `.ai/assets/tech-stacks/dotnet-backend/references/BUILDING-BLOCKS-CLASS-INDEX.MD` | .NET backend building block reference |
| `.ai/assets/skills/` | Canonical skill specs |
| `.ai/assets/sub-agent-role-prompts/` | Canonical sub-agent role prompts |
| `.ai/scripts/` | 過渡期 AI workflow scripts、context governance checks 與本機工具 orchestration helpers |

### Project Knowledge and Governance (`.dev/`)

| Path | 說明 |
| :--- | :--- |
| `.dev/README.MD` | Human-facing project knowledge purpose 與 boundary guide |
| `.dev/INDEX.md` | Project knowledge 檔案與目錄索引 |
| `.dev/ARCHITECTURE.md` | 以證據重建的目前產品架構 |
| `.dev/project-config.yaml` | 產生自本 repo facts 的 inventory |
| `.dev/standards/` | Governance、context、workflow、coding、review 與 structure standards |
| `.dev/guides/` | Human-facing guides |
| `.dev/adr/` | ADR governance and retained decisions |
| `.dev/requirement/` | Requirements and requirement authoring materials |
| `.dev/domain-language/` | 領域統一詞彙範本與目標 repo 詞彙收納區 |
| `.dev/specs/` | Specification organization and retained specs |
| `.dev/operations/` | Operations docs and operations document guides |
| `.dev/workflows/` | Workflow artifacts |

### Runtime Skill Wrappers

| Path | 說明 |
| :--- | :--- |
| `.agents/skills/README.md` | Current runtime wrapper index |
| `.agents/skills/<skill>/` | Current runtime skill wrapper |
| `.claude/skills/README.md` | Claude-compatible wrapper index |
| `.claude/skills/<skill>/` | Claude-compatible skill wrapper |

### 產品與 Tooling 根目錄

| Path | 說明 |
| :--- | :--- |
| `MQArchLab.slnx` | 包含 bounded-context 與 product test projects 的 solution |
| `src/` | Products、Orders、Inventory、shared contracts、building blocks 與空的 Shared Kernel placeholder project |
| `tests/` | Products 與 Orders 的 product/domain tests |
| `tools/` | Roslyn architecture analyzers 與 runtime validation tooling |
| `docker-compose/` | 本機產品、database、broker 與 observability topology |

## 語言規則

- Agent-facing context 應優先使用英文，除非來源材料本質上就是 human-facing 繁體中文。
- Human-facing guides 與 README content 應優先使用繁體中文台灣用語。
- Runtime wrappers 應保持輕量，並指向 canonical specs。
- Context 分類優先使用資料夾位置，而不是每個檔案各自加 metadata。

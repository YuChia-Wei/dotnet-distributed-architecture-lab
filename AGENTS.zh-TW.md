# AGENTS.md

[English](AGENTS.md)

本文件是 distributed-commerce lab 的繁體中文（台灣）協作指南，英文版 `AGENTS.md` 為 canonical 版本。子目錄中的 `AGENTS.*` 管轄其自身範圍。優先順序為：使用者直接授權、較深層指南、本指南、其他一般文件。

## 專案與框架權威

本 repo 是 .NET 分散式商務架構實驗室。Products、Orders、Inventory 與 Procurement 是目前四個業務 bounded context。SupplierSandbox 與 SupplierMock 是外部系統範例；兩個 Vue 前端及 YARP 是現行應用介面。產品事實應核對 `MQArchLab.slnx`、專案檔、原始碼、測試、Compose 與目前 `.dev/` 專案紀錄。`.dev/project-config.yaml` 是產生的 inventory，與上述來源不符時應以來源為準。不得把框架來源 repo 的產品事實帶入本目標。

[目前框架契約](.dev/ai-context/CURRENT-FRAMEWORK.md) 標示選定的安裝與保留的開發編排恢復證據；既有 main 採用保留於 [RC3](.dev/ai-context/RC3-MAIN-INTEGRATION.md) 與 [RC4](.dev/ai-context/RC4-MAIN-INTEGRATION.md) 整合證據。[目標工程規則](.dev/ai-context/TARGET-ENGINEERING-RULES.md) 持有保留的十四條完整規範、二十條請求路由、四項客製化及目標 Git 邊界。已安裝的 skills 與 common/.NET knowledge 有別於目標採用。Package 或 wrapper 本身不證明規則適用，也不證明驗證通過。官方 lock 由 installer 持有，不得手改。Managed packages 只能使用實際安裝宣告的已儲存固定候選與 Codex、Claude 原名入口。負責人另選擇 `.ai/custom/skills/` 下的 project-owned `standards-promotion-experimental@0.1.1-alpha.1` 副本；明確選定試驗時使用其獨立實驗入口。副本工具保留 `standards-promotion` operation/config namespace。此副本不屬於官方 lock 或發布成品，用途與行為驗收仍待完成。負責人曾於 2026-10-01 授權先前恢復工作整合至 main 並推送。2026-10-04 請求選擇在 `codex/2026-10-04-framework-019-init` 本機安裝正式版 `0.19.0`，並試用 `ai-context-init@0.2.0 initialize`；不延伸歷史整合或推送授權。

歷史上，Issue #22 的負責人授權一次性的 RC2 破壞性替換，並明確延後 S6、runtime 與升級／還原試驗。這些檢查應記為 `deferred-by-owner`；靜態檢查不能當成行為驗收。此例外不恢復或啟用 CI。歷史 RC1 metadata、wrapper 與備份不是目前權威。

## 產品決策

- Inventory 使用 EF Core 與其選定的庫存／預留 outbox 邊界。Products 與 Orders 維持 Dapper。Orders 選用 event sourcing。Procurement 與供應商實驗有各自目前的需求及操作指南。
- 保留具有可辨識 Given-When-Then 語義的純 xUnit v3 測試，以及明確的 BDDfy opt-out。Moq 或 NSubstitute 依各測試專案實際設定選擇。
- 已退役的 analyzer 與 runtime-validation 專案維持停用。可重用範例、source include 與 template 在本目標另行採用前都是指引。
- 保留目標 Issue-first 授權、LF policy、限定目錄的 `.codex/agents` 追蹤、實際 AI 歸屬，以及目標權威所述的唯一歷史 Git 例外。

## 漸進載入與路由

從請求、Git/worktree 狀態、本指南及具名 Issue／artifact 開始。需要產品事實時，再讀 `.dev/ARCHITECTURE.md`、`.dev/project-config.yaml`、相關需求／規格及操作指南。透過[現行技能索引](.dev/ai-context/skills.md)選擇一個 skill 或 operation，讀取其已安裝入口與必要參考。AI context 變更須讀 `.dev/standards/AI-CONTEXT-BOUNDARY.md` 與 `.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md`。程式碼探索優先使用可用且新鮮的 code graph，實質結論仍須以 Git-tracked 檔案核對；graph 無法使用或不完整時再直接搜尋。

AI context 治理與遷移使用 `ai-context-governance`；稽核使用 `ai-context-auditor`。架構、GWT 設計、code review、需求、規格、problem frame、實作及相容性驗證使用對應的選定 skill。決策、lesson 與 PR 作者流程分別使用 `adr-author`、`lesson-author` 與 `pr-author`。需要多階段開發與專業 skill 交接時使用 `software-development-orchestrator`；目標 workflow 政策及 `.dev/workflows/` 仍擁有紀錄格式與整合權限。通用 skill 指示不會默默取代目標 .NET knowledge 或有效規則的適用條件。執行 .NET 工作前，解析適用的目標權威與選定的 knowledge binding；專項涵蓋不足須如實說明。選定的 `ai-context-init@0.2.0` 在請求時補齊協作基礎或更新選定的專案事實；重複初始化是依既有內容語義檢查缺口，安裝本身不會執行它。舊 `adr`、`lesson`、`pr`、legacy init 與 `ai-context-upgrader` 實作維持退役。

## Workflow、Git 與驗證

變更 source-of-truth、AI context、路由或多階段工作時，使用 `.dev/standards/WORKFLOW-GATE-POLICY.md`。Workflow mode 須依 `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md`、`.dev/TEAM-GIT-FLOW-RULES.MD`，並在實質編輯前使用專用分支。Commit 依 `.dev/standards/GIT-COMMIT-POLICY.md` 及其 YAML 權威；有適用 validator 時，commit 前以檔案驗證完整預定訊息。AI model/runtime 歸屬須反映實際執行；RC1 固定雜湊 target validator 已退役，目前未設定新的目標本地自動 commit validator。

先定義可觀察驗收條件，再執行最小有意義的檢查。如實回報 `passed`、`failed`、`blocked`、`deferred` 與 `not-applicable`。獨立審查、CI、runtime 執行、package 安裝、目標規則採用、push、PR、merge、Issue／Project 狀態、tag 與發布是不同狀態。套用框架變更前須調和目標自有權威。保留無關修改、使用者資料與歷史證據。Fixture 或靜態結果不得充當實際產品／runtime 證據。

## 導覽與語言

`.ai/` 包含選定的受管理 skill 與 knowledge package、明確的專案設定及 installer 持有的 lock。`.agents/skills/` 與 `.claude/skills/` 是 runtime 探索入口。`.dev/` 包含產品事實、標準、目標權威、操作、workflow 與人類指南。`README.md` 是繁體中文產品入口；`README.en.md` 是英文版；`CLAUDE.md` 是簡薄的 runtime 指引。

Agent-facing 執行契約優先使用英文；human-facing 指南可用繁體中文（台灣）。`AGENTS.zh-TW.md` 必須與英文版在結構和規範上保持一致。Runtime 入口是已安裝 package 的投影，不是第二套語義權威。

## 專案閱讀地圖

| 工作 | 相關時閱讀 |
| --- | --- |
| 理解產品目的與邊界 | [產品 README](README.md)、[需求概覽](.dev/requirement/distributed-commerce-bounded-context-overview.md)、[架構](.dev/ARCHITECTURE.md) |
| 修改行為或測試 | [行為基準](.dev/requirement/reconstructable-system-baseline.md)、相關[領域](.dev/specs/domains/)與[測試](.dev/specs/tests/)規格、[目標規則](.dev/ai-context/TARGET-ENGINEERING-RULES.md) |
| 選擇協作政策或檢查權責 | [政策索引](.dev/standards/INDEX.MD)、[專案驗證設定](.dev/project-config.yaml)、適用的操作指南 |
| 開始有限範圍的唯讀或小型文件工作 | [第一項工作指南](.dev/guides/first-task.md)，包括指令來源、工作目錄、必要條件與尚未執行狀態 |
| 尋找專案紀錄或框架資源 | [專案索引](.dev/INDEX.md)、[AI 資源索引](.ai/INDEX.MD) |

第一項工作指南不會執行其中範例。產品指令在實際執行被記錄前，僅屬已發現的操作指示；目標 framework admission、routine local 與 CI gates 仍依專案設定維持未設定。

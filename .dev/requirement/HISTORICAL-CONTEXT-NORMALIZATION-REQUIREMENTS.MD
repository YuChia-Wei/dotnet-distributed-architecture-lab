# 歷史 Context 與範本正規化需求

## Metadata

- Version: 0.1
- Date: 2026-07-04
- Owner: YuChia-Wei
- Status: Approved for implementation

## 背景

本 repository 是 AI 協作知識庫與可重用 context framework，不是 `dotnet-mq-arch-lab` 或 distributed commerce 產品 repository。

目前仍有部分舊產品資訊被放在正式 project truth 路徑，包括 domain specs、test specs、problem frames、operations 文件、`project-config.yaml`、Products / Orders / Inventory bounded contexts、SaleOrders / SaleProducts namespaces、固定本機連線資訊，以及 frontend stack 設定。

這些內容需要被刪除、範本化或移到明確標示的未來規劃文件，避免 AI Agents 將其視為目前產品真相。

## 目標

- 清除舊產品名稱、bounded contexts、namespace 與 runtime topology。
- 將可重用內容整理成中性的範本。
- 已有 canonical template 可涵蓋的舊 domain specs、test specs、problem frames 與 operations truth 直接移除。
- 將 `project-config.yaml` 定義為 `repo-structure-sync` 依目標 repo evidence 產生的 target-repository artifact。
- 移除固定 credentials 與 connection strings，範例改用 placeholders 或環境變數。
- 保留 React / Vite 作為未來多語言、多技術棧 context 分類的簡化參考，但不得出現在目前 dotnet-backend project truth。

## Functional Requirements

### FR-1：歷史 Product Truth 分類與清除

下列內容必須盤點為 `remove`、`convert-to-template` 或 `retain-as-explicit-example`：

- `.dev/requirement/` 的舊產品需求。
- `.dev/specs/domains/` 與 `.dev/specs/tests/` 的舊產品規格。
- `.dev/problem-frames/` 的非 template use case。
- `.dev/operations/` 的 product-specific context map、event catalog、MQ topology 與 runbook。
- `.dev/BUILDING-BLOCKS-CLASS-INDEX.MD` 與 guides 中的舊專案名稱或路徑。

若現存 guide、template 或 schema 已涵蓋相同行為，舊產品 artifact 應直接移除。

### FR-2：移除舊產品識別

Active context 不得再將下列名稱描述為目前 repository truth：

- `dotnet-mq-arch-lab`
- `Products`
- `Orders`
- `Inventory`
- `SaleProducts`
- `SaleOrders`
- `InventoryControl`
- 舊專案專用 queue、topic、host、port、database 或 container 名稱

通用教學中若需要示例，應改用 placeholders，例如 `<BoundedContext>`、`<Aggregate>`、`<Event>`。

### FR-3：Project Config 由 Repo Structure Sync 產生

- `.dev/project-config.yaml` 是目標 repository 的 machine-readable project truth，不是 framework 固定設定。
- Canonical template 應由 `repo-structure-sync` 擁有。
- `repo-structure-sync` 必須依 solution、project、package、infra 與 user-confirmed facts 產生或更新 `.dev/project-config.yaml`。
- 空 repository 不得被填入虛構 bounded contexts、database、broker、frontend 或 deployment facts。
- Framework repository 本身不得保留舊產品的 `.dev/project-config.yaml`。

### FR-4：Credentials 與 Connection Strings

- 固定 password、username、database、port 與 connection string 不得作為可複製預設值。
- 範本應使用 `${ENV_VAR}`、`<placeholder>` 或明確的 local-example marker。
- 不得將示範 credentials 描述為 production recommendation。

### FR-5：Frontend 與未來多技術棧規劃

- React / Vite 不屬於目前 dotnet-backend profile。
- 應保留一份簡化的人讀文件，說明未來 frontend、其他語言與 full-stack context 可如何分類。
- 該文件必須標示為 exploration / future planning，而不是目前支援承諾。
- 不建立 frontend skill、frontend profile 或產品 frontend config。

### FR-6：Workflow 與 Requirement 狀態正規化

- 已完成 task 的 workflow 不得持續標記為 `active`。
- 舊格式沒有 plan status 的已完成 workflow 應補上完成狀態或 completion note。
- 已實作 requirement 應補 implementation outcome，保留原始需求與決策歷程。

## Non-Goals

- 不建立產品 domain vocabulary。
- 不建立 frontend implementation skill。
- 不建立 full-stack template。
- 不處理 technical glossary。
- 不在本 workflow 執行 analyzer replacement phase 2。

## Acceptance Criteria

- Active context 不再將 distributed commerce、Products / Orders / Inventory 或 SaleOrders / SaleProducts 視為目前產品真相。
- 舊 domain/test specs、problem frames 與 operations truth 已移除或明確範本化。
- `.dev/project-config.yaml` 的 canonical template 與產生責任已整合到 `repo-structure-sync`。
- Framework root 不再保留舊產品 project config。
- 固定 credentials 與 connection strings 已從 active reusable templates 移除或改為 placeholders。
- React / Vite 僅存在於明確標示的 future multi-stack context placement guide。
- 已完成 workflow 與 requirement metadata 不再呈現未完成狀態。
- JSON、YAML、reference search 與 `git diff --check` 驗證通過。

## 已確認決策

| 決策 | 結論 |
| --- | --- |
| 舊 specs / tests / problem frames | 當作範本候選；與現有範本重複時直接移除 |
| `.dev/project-config.yaml` | 由 `repo-structure-sync` 依目標 repo facts 產生 |
| 舊產品名稱 | 從 active context 移除 |
| 固定 credentials / connection strings | 移除或 placeholder 化 |
| React / Vite | 從目前 project truth 移除；保留為未來多技術棧收納規劃參考 |

## Recommended Workflow

1. `dev-workflow`：建立 task streams 與 commit checkpoints。
2. `ai-context-governance`：分類、移除、範本化與 index sync。
3. `repo-structure-sync`：建立 project-config template 與產生規則。
4. `ddd-ca-hex-architect`：只有在保留範例的 DDD 語意不清楚時介入。

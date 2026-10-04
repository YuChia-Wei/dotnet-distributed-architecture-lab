# 開始第一項有限範圍工作

先讀 [AGENTS.md](../../AGENTS.md)、[產品 README](../../README.md) 與
[專案索引](../INDEX.md)，確認本次問題、允許修改的範圍及實際授權。
依 `AGENTS.md` 與本次選定 skill 的實際操作契約執行有限任務，並按條件套用
[目標工程規則](../ai-context/TARGET-ENGINEERING-RULES.md)。本指南不會自動啟動以下範例。

## 範例一：唯讀理解 Inventory 庫存預留

可提出以下具體請求：

> 請唯讀說明 Inventory 的 ReserveInventory 流程。先讀
> `.dev/requirement/reconstructable-system-baseline.md`、
> `.dev/specs/domains/inventory-item/usecase/reserve-inventory.json`、
> `.dev/specs/tests/inventory-item/use-cases/reserve-inventory.test-spec.md`
> 及 `.dev/operations/inventory-efcore.md`，再核對規格列出的實作與測試。
> 說明首次成功、相同 OperationId 重送、payload 衝突、交易和 outbox 的責任。
> 引用支持結論的檔案，分開描述預期行為、原始碼觀察與實際執行證據。
> 不修改檔案、不執行產品測試或啟動服務、不進行外部寫入；缺漏或矛盾請直接列出。

[Use-case 規格](../specs/domains/inventory-item/usecase/reserve-inventory.json)
列出 Application port、Infrastructure adapter 與測試證據路徑。
[測試規格](../specs/tests/inventory-item/use-cases/reserve-inventory.test-spec.md)
保留案例與歷史執行範圍；歷史通過不能證明目前 revision 的 runtime 行為。

程式碼探索優先使用可用且新鮮的 code graph，再以來源檔核對。
graph 缺少 revision、新鮮度或相關節點時，記錄限制並直接查驗具名檔案。
此工作可由一般唯讀工具完成，不需要新增 specialist 或 package。

## 範例二：補上一個既有操作指南入口

2026-10-04 初始化時，`operations/README.MD` 的現有文件入口尚未列出
`inventory-efcore.md`。這是一項可另行選定的小型文件變更；本次初始化保留該文件原文。
在確認本次 work-item binding 與寫入授權後，可提出：

> 請只修改 `.dev/operations/README.MD`，在既有操作文件入口補上
> 連結文字為 `Inventory EF Core 指南`、相對目的地為 `inventory-efcore.md` 的連結。
> 以現有 `.dev/operations/inventory-efcore.md` 為依據，保留其他文字、
> 產品行為與歷史證據。若連結已存在且正確，回報無需修改。
> 確認相對連結可解析，從 repo 根目錄執行
> `git diff --check -- .dev/operations/README.MD`，並回讀完整 diff。
> 回報實際改動與檢查結果；不 commit、push、啟動服務或執行產品測試。

完成條件是既有指南可從 operations 入口找到，其他內容不受影響。
一般授權文件工具足以處理；本範例不要求安裝新工具，也不替之後的執行取得授權。

## 指令來源、前提與狀態

以下均以 repository 根目錄為工作目錄。指令列在文件中不表示已執行；
本次初始化的實際檢查由 [試用結果](../workflows/2026-10-04-framework-019-init/results.md) 記錄。

| 指令或檢查 | 來源與前提 | 本指南的狀態 |
| --- | --- | --- |
| `git diff --check -- .dev/operations/README.MD` | 上述已界定的文件變更檢查；需 Git checkout，套用於該次 diff | `discovered`；範例未執行 |
| `dotnet test tests/InventoryControl.Tests/InventoryControl.Tests.csproj` | [Inventory 操作指南](../operations/inventory-efcore.md)；需符合 [global.json](../../global.json) 的 SDK 與套件還原能力；外部 PostgreSQL 測試另依 [tests/README.md](../../tests/README.md) opt-in | `discovered`；初始化未執行 |
| 目標 framework admission、routine local 與 CI | [project-config.yaml](../project-config.yaml) 的既有選擇 | `not-configured` |

上述產品測試指令供之後明確選定的驗證工作使用，不是唯讀或文件範例的必要步驟。
外部測試 skipped、文件檢查通過及框架安裝完成都不能當成產品 runtime 驗收。

## 結束條件

交付內容須回答已選定請求、保持檔案與操作範圍，並清楚列出實際查驗和未知事項。
初始化到可使用的入口、權威來源與下一項有限工作為止；後續開發、驗證或整合另依實際請求進行。

# Framework 0.19.0 升級至 0.21.0

2026-11-11，Windows x64。這次升級建立後續工作的本機基線。試裝分支為 `codex/framework-021-upgrade`，從 `main` 的 `7a0bff401bea86428b5c24eab6362ef2170d20d7` 建立。起始 lock 是 `0.19.0`，418 個受管理檔案皆符合雜湊。

## 成品與選擇

使用 `v0.21.0` 的公開成品，來源 `5fe8d307ce8c337463088f2abb4f2a945262a56d`，tag object `2aef3ecff598be21252d9af4850acbcaf511f51e`。ZIP SHA-256 為 `a20e4c106c2974f525654ac7895149f0b87d35a34a61e50cd9ac313975c6465e`。核對 manifest、校驗檔、497 個 ZIP 成員及 Engine pin 後，以封包內 Engine 2 執行 `derive-subset`、`inspect`、`plan`、`apply` 和安裝後讀回。[0.21.0 成品](https://github.com/YuChia-Wei/ai-collaboration-framework/releases/tag/v0.21.0)

- 將 `bdd-gwt-test-designer` 換成 `test-designer`。原 `ddd-ca-hex-architect` 的領域與架構工作分別對應 `domain-model-designer` 和 `software-architect`。本版保留 `local-backlog` 與專案現有設定。
- 選取 19 個 skills、`dotnet-backend@0.1.6`、`engineering-common@0.4.0` 及 Codex 和 Claude 原名入口。既有 40 個 bindings、technology profile、規則 ID 和目標規則檔完整保留。雙語根入口和 README 更新至本版，`AGENTS` 亦更新所記錄的 `ai-context-init@0.2.5`。
- 兩個成品試驗分支各自從原始 `0.19.0` 開始。此報告只涵蓋正式版路徑。

## 驗證

- Engine 回傳 `applied`。Plan 有 39 新增、78 變更、13 移除與 327 保留的 managed paths，另包含五份專案安裝選擇及入口編輯。安裝後 444 個 managed files 零漂移。Lock SHA-256 為 `e2f78631bedb3016cfe1c7afaae4c818141f58f8febec7cddbf30b9dd26c9b36`。
- 讀回 278 個資源項目、40 個 bindings 和 40 個 authority SHA-256，並確認 38 個 Codex 和 Claude 入口連到已安裝的對應 skill。抽查的現行入口和目標規則內，指向知識套件的連結都可解析。比對 plan 範圍外的 1,392 個已追蹤檔案，內容雜湊一致。
- Windows x64、SDK 10.0.404，`InventoryControl.Tests` 在升級前後皆為 37 通過、24 略過、0 失敗。外部服務未 opt in。實際 AI runtime discovery 與外部服務驗收未執行。

本次用 merge commit 將安裝和入口調整作為一組納入本機 `main`。原始操作與測試輸出保留於本機 `artifacts/aicf-20261111/`。Engine 的復原紀錄位於 `F:/a21u/r/`，其 process-termination 復原範圍限於磁碟資料仍存在時。回查舊版可由起始 commit 建立獨立 checkout。

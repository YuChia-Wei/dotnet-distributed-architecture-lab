# Development Review Report

## Template Metadata
- template_id: `software-development-orchestrator/development-review`
- template_version: `1.1.0`
- template_created_at: `2026-07-10T18:25:11+08:00`
- template_updated_at: `2026-08-05T02:12:00+08:00`

## Report Metadata
- workflow_id: `2026-09-12-nuget-and-consumer-parallel-examples`
- report_id: `development-review-2026-09-12-nuget-and-consumer-parallel-examples`
- owner_skill: `software-development-orchestrator`
- related_plan_id: `development-plan-2026-09-12-nuget-and-consumer-parallel-examples`
- status: final
- created_at: 2026-09-12T14:41:50+08:00
- updated_at: 2026-09-12T14:41:50+08:00
- template_source: `.ai/assets/skills/software-development-orchestrator/templates/development-review-report-template.md`
- template_version: `1.1.0`
- workflow_locator: `.dev/workflows/2026-09-12-nuget-and-consumer-parallel-examples/workflow.yaml`

## Scope
本次為已授權實作的交付檢查與驗收彙整。產品、測試與 Compose 執行版本為 `3f2f93dcde8faede6704a0b44ce1a575ea729634`；後續 closeout commit 僅記錄 workflow 證據。NuGet 盤點涵蓋 27 專案、18 個具有套件參照的專案、30 個目前直接套件 ID／128 筆參照。原始 29 個 ID／122 筆參照中，xunit 被替換，另新增六個 RuntimeCompilation 參照。

不含 RabbitMQ 實機驗證、持久化 local queue、跨重啟 exactly-once、負載基準、push、PR、merge、Issue closure 或 release。原始外部事件至兩個 handler 的工作不是新增另一種本機事件。

## Findings
最終產品檢查未發現未處理的 CRITICAL、MUST FIX 或 SHOULD FIX；8 項適用檢查均符合本次教學範圍。先前 Controller action injection 已改為建構式注入；缺少 runtime compiler 的啟動錯誤已由六個明確 package references 修正；正式商務 E2E 找出的 Inventory scoped factory 問題已以單一型別 allow-list 修正。

| Selected route / check | Comparison | Outcome |
| --- | --- | --- |
| use-case / dependency direction | 兩項獨立 use case 只依賴各自 port；輸入不攜帶 MQ framework | passed |
| handler / WhenAll | 每項工作建立獨立 async scope，等待完成與 disposal；使用者要求的教學協調入口例外已記錄 | passed |
| reactor / original external event | 兩個不同 handler 同樣接收 IndependentWorkRequested；framework 分派至兩條 sticky queue | passed |
| controller / HTTP | 建構式注入、202 僅代表發佈接受、輸入錯誤 400、預設未啟用 | passed |
| configuration / Wolverine 6 | 六個 host 有 RuntimeCompilation；Inventory 只允許 IInventoryReservationOutbox，global policy 保留 NotAllowed | passed |
| test / concurrency and retry | deterministic gate 驗證真正重疊；Kafka 成功分支 1 次／失敗分支 2 次，WhenAll 則兩者重跑 | passed |
| test / cancellation and scope | 同步拋錯仍等待另一分支；取消與每次 scope disposal 有測試；新測試保留 GWT | passed |
| package / compatibility | ASP.NET 10 相容 OpenApi 2.12.2；xunit.v3.mtp-off 保留 VSTest；預發行與遞移版本限制分別列出 | passed |

Review routes: use-case, handler, reactor, controller, test, general-csharp. Rule resolver selector: initialized-target / review / direct / dotnet-backend / dotnet-mixed-review；實際輸出保留於 `artifacts/nuget-consumer/review-rules.yaml`。Domain aggregate/event-sourcing 改造不在本次範圍，不套用新的 aggregate gate。

## Validation
最終 `mqarchlab-pr5-integration` 的五個測試專案共 **92 passed / 0 failed / 0 skipped**：Inventory 33、Orders Domain 13、Orders 11、Products Domain 9、Products 26。包含 3 個 PostgreSQL 與 4 個 Kafka 實際整合測試；新範例共新增 12 個 test cases。受控失敗測試替換 outbound writer，外部訊息仍經真實 Kafka；這與正式 Consumer E2E 的真實 demo adapter 證據分列。

正式 E2E：兩種模式均經 gateway → Product API → Kafka → Orders Consumer，兩分支重疊、scope 不同，重送不重複產生程序內副作用。商務 E2E 驗證產品建立／查詢、庫存 10 → 8、下單、出貨／交付、另一筆取消及庫存不足拒絕。取消現行不回補庫存，拒絕前後庫存均為 7。

NuGet 的直接＋遞移漏洞與棄用查詢均涵蓋 27 專案，回報 0 packages／0 problems。直接 outdated 保留 OpenApi 3.x 相容限制，兩個只有預發行版本的 instrumentation 使用官方 metadata 判定。遞移 stable-only 查詢發生 CLI 的 `Sequence contains no matching element`；include-prerelease 查詢成功、仍列出 89 個有較新候選的間接套件 ID（其中 37 個候選沒有預發行字尾）。它們由上游直接套件解析，本次未新增強制間接版本覆寫，不能宣稱全部相依性均為 latest。

建置保留 18 個警告（既有 nullable 與新版 xUnit analyzer 提示），0 errors。先前失敗紀錄保留在 ignored artifacts：SDK 快取過舊、BuildKit snapshot、sandbox 暫存權限、首次 Inventory E2E；定向更新基底／無快取循序建置、正常 Windows 權限及具體程式修正後重驗通過，未把原始失敗改寫為成功。

單元／整合／E2E provider 為 target-profile-commands。Routine policy 維持 local manual；本次命令由使用者需求與 workflow 明確選取。Spec compliance 未選用，not-applicable。既有 Compose volumes 保留；額外 Kafka 已停止，臨時 regression runner 使用 --rm。

### Acceptance projection
下表直接投影 `evidence/acceptance-ledger.json`，識別碼、結果與 output bytes SHA-256 完全一致。實際 receipt 與 output 位於 ignored `artifacts/nuget-consumer/`；他機需重跑，缺檔不構成 passing evidence。

| Acceptance | Issue | Outcome | Evidence SHA-256 |
| --- | --- | --- | --- |
| NUGET-REGRESSION | #10 | passed | `178db73a830aefd3ec372cf055e35850a40463e96aa87c79208fbdc7d1ab310c` |
| NUGET-VULNERABLE | #10 | passed | `06a1b718ddc548e962eaf72602595dc40e274826c34f26e828ba9db4eca3830b` |
| NUGET-DEPRECATED | #10 | passed | `38b421419eaf49a87d6a0ceb2e9fd6edd8c577767a60c516f877b37d58602965` |
| MQ-WHENALL | #11 | passed | `1780553c2a819a94535e80cf79cc8ed938e6a48a8e083fea102b72a084b9043b` |
| MQ-TWO-HANDLERS | #11 | passed | `1780553c2a819a94535e80cf79cc8ed938e6a48a8e083fea102b72a084b9043b` |
| MQ-RETRY-ISOLATION | #11 | passed | `178db73a830aefd3ec372cf055e35850a40463e96aa87c79208fbdc7d1ab310c` |
| COMMERCE-REGRESSION | #10 | passed | `44220904864795d0da2ebe1f9b1a9a3183f9a3feb4db1c3fdf3aec6762dad6e7` |
| NUGET-MATRIX | #10 | passed | `3b47d92fc67da2fdf05dd5951a05aae874e4bfcbbd77c2fe62433a0129f02e7f` |

## Role Execution Integration
實作 role records 位於三個 tasks。適用的 reactor/controller/profile/usecase-test/reactor-test 由 `/root` inline 執行；研究子代理僅提供唯讀套件、API、現況與工具 schema 證據。沒有將研究代理宣稱成正式實作或 reviewer。Code-review 的 general/controller/reactor bindings 由主代理直接執行，aggregate binding 不適用；完整紀錄附於 DEV-003。

## Decision
- Result: approved for local implementation delivery.
- Residual limits: lab-only in-process deduplication; local queues do not add restart durability; RabbitMQ remains unverified; upstream-resolved transitive versions remain.
- Completed commits: implementation `81a2936`, HTTP/documentation checkpoint `1354568`, runtime compatibility repair `3f2f93d`; the containing closeout commit records evidence only.
- Online Issues #10 and #11 stay OPEN. No push, PR, merge or release performed.

# 採購實驗驗收紀錄

Workflow: `2026-09-26-procurement-supplier-lab`。Issue: [#17](https://github.com/YuChia-Wei/dotnet-distributed-architecture-lab/issues/17)。Coordinator 已完成選定範圍的 code review、修復及 runtime/UI 驗收。27/27 個原定情境與 AC01–AC06 均有適當層級的實際證據，判定 compliant-within-scope；這是規格涵蓋率，不是程式碼覆蓋率。使用者最後審核、push、main merge、PR 與 Issue 結案是另外的決定。

## 證據與執行主體

實際輸出保存於 [evidence/manifest.json](evidence/manifest.json)，含每份原始檔 SHA-256；[test-results-summary.json](evidence/test-results-summary.json) 從原始 TRX 擷取每項結果與錯誤，沒有把 skipped 改成 passed。規格與模型輸入基準是 `7259397`。所有子代理的修復、coordinator 協助及首輪失敗見 [review-and-model-observations.md](review-and-model-observations.md)。

| 執行 | 實際主體 | 結果與使用界線 |
| --- | --- | --- |
| 首次採購 PostgreSQL | 原始 worker `79437e8`，整合 checkout `c757dfd` | 20 pass、1 fail、0 skip；Dapper timestamp materialization 失敗保留。 |
| 完整 solution regression | `6e318bc`；image `sha256:da89a2544d3157f0142f84ec6f2d04c284407db54f76764f0b72ad09a8d771ad` | 175 pass、2 fail、4 skip。Inventory 64 pass；Products、Orders 通過。兩個採購失敗後續修復；四個未配置的 EF/Wolverine sample external cases 仍為 skipped。 |
| 修復後採購 PostgreSQL、供應商 tests | `4763ada`（相同 tree 的新 commit `7b19968`）；image `sha256:ac22b8129e3f0a520b710034e8d5ae82c33462dc0b96676c38ea956708959224` | 採購 39、Sandbox 2、WireMock 2 全部 pass，0 fail、0 skip。採購含 10 個實際 PostgreSQL tests。後續供應商控制修正須另測。 |
| 首次整合 HTTP | 採購 `cabd056` 修復及 Supplier `47db2c3` | 12 pass、5 fail；Microcks 匯入成功但 dispatcher／proxy body 不正確。 |
| 修復後整合 HTTP | `4763ada` | 17 pass；原生兩個引擎各自 mock、proxy、hybrid 與 request provenance 通過。 |
| 最終 supplier container tests | `35589b8`；image `sha256:67a83a2714264102f925484238f94f146807977109c8fe0012ce3c04848b9ef6` | Sandbox 2、WireMock 4 全部 pass，0 fail、0 skip；包含實際 PostgreSQL、原生 HTTP、reset 故障／取消／恢復及數值精度。 |
| 最終 HTTP與UI | `35589b8` | 原有17項＋補充15項全部通過；三個UI已實際操作，Microcks原生Save成功。證據為 http-contracts-final、supplemental-http、browser-verification。 |
| 直接採购／收貨 | `direct-flow.json` 與同 identity 的持久化帳本讀回 | 初始 stock20，接單不增庫存，qty6 結果26，qty4 結果30；相同收貨重播不再入庫。帳本讀回補充原始摘要未列出的26 checkpoint。 |
| Kafka 中斷恢復 | `broker-recovery.json`；03:30 左右的實際部署，早於時間精度修復 | 同一已核對 project/service 的 Kafka 容器停止時 receipt201 已持久化、庫存30；恢復後33、重播仍33。此證據僅重用於未改變的 outbox／broker／Inventory 路徑；之後的時間精度修復由實際 PostgreSQL及 event payload equality tests另證。 |

Git policy 首次檢查發現三筆未發布 commit 的章節標題放在內文同一行。修復只改 commit metadata，四筆受影響 parent chain 的 tree 全部保持相同；原始 branch 留存，old/new 對照見 [commit-message-repair.json](evidence/commit-message-repair.json)。實際測試的原 SHA 不會被冒充成後來執行。

## 逐項契約對照

以下 source 測試名稱以實際 TRX 同名結果及 test source 對應；所有列出的原定情境均已完成，保留上表不同執行主體的使用界線。

| 範圍 | 實際 assertion 與證據 |
| --- | --- |
| P01 | `PurchaseScenarios.Accepted_purchase_uses_original_client_key`；HTTP P02 建單及直接採購流程證明本地／供應商識別綁定。 |
| P02 | `Matching_replay_returns_same_purchase_without_resubmission`、`Concurrent_matching_creates_store_one_purchase`；HTTP 201/200、同供應商 ID、上游 POST delta1。 |
| P03 | `Changed_payload_conflicts_before_supplier_call`、實際 PG `Changed_quantity/provider/product_conflicts_against_postgres_without_supplier_call`；HTTP 三個409及原始資料不變。 |
| P04 | HTTP post-commit delay4000ms，202 SubmissionUnknown，GET 供應商存在，reconcile200 Accepted，上游 POST delta1；`Reconcile_not_found_keeps_unknown_without_resubmission`。supplemental P04 使用已初始化商品，實際 Inventory 前後值相同、零 receipts。 |
| P05 | `Invalid_http_result_never_claims_supplier_acceptance` 四筆5xx／malformed／mismatch／unknown status；`Malformed_provider_response_is_unknown`、`Late_transport_failure_preserves_accepted_order`。 |
| P06 | `Rejected_purchase_forbids_receipt`；`denied-order.json` 實際 DENY-001 持久化 Rejected／穩定重播／收貨409／stock不變。供應商 HTTP400/422 輸入錯誤不冒充已驗證的 terminal Rejected；只有合法供應商訂單的 rejected 狀態才轉為 Rejected。 |
| P07 | `Invalid_purchase_fails_before_io` 與 HTTP P07，所有非法 input400、上游 POST delta0、無新供應商單。 |
| R01 | `Two_partial_receipts_complete_the_order`、direct-flow與[兩筆實際帳本](evidence/direct-flow-ledger-readback.json)：stock20→26→30，重播不增量。 |
| R02 | `Invalid_second_receipt_preserves_prior_six`（5/0/-1）、PG `Invalid_follow_up_receipts_leave_postgres_facts_unchanged`，receipt／outbox／aggregate不變。 |
| R03 | PG `Replay_after_source_outbox_deletion_does_not_recreate_event`、Inventory同條件 R03、Kafka恢復後重播；永久帳本保留結果且不重建事件。 |
| R04 | PG `Receipt_id_cannot_move_to_another_purchase_or_product`、Inventory R04 immutable payload tests、domain quantity conflict。 |
| R05 | PG `Concurrent_matching_receipt_has_one_commit`、Inventory同ReceiptId並行 tests；`New_receipt_timestamp_is_utc_millisecond_precision` 與 source event equality 確認初次／儲存／重播時間完全一致。 |
| R06 | PG `Receipt_transaction_is_durable_and_race_safe`、`Concurrent_receipts_never_expose_mixed_read_snapshot`；一個收貨競爭者成功，另一個因超量或完成狀態拒絕。 |
| R07 | Inventory實際 PG missing_stock/retry、outbox_staging_failure/retry、overflow/no_effect，沒有殘留 claim／stock／outbox。 |
| R08 | 實際 Kafka停機／恢復與兩種outbox觀察；source published_at只表示交接給持久化transport，最終stock和ledger證明消費。 |
| S01 | `SupplierSandboxTests.S01...` 實際PG，加HTTP並行／重播200／改payload409／lookup同ID。 |
| M01–M06 | `http-contracts-final.json` 兩引擎各6情境：origin、Sandbox request增量及實際path/body。supplemental 另外驗證固定payload四欄位變更在hybrid走上游、mock-only不走上游、不冒用固定接單，以及實際Procurement兩個profile。unknown route不宣稱通用proxy。 |
| U01–U03 | `browser-verification.json`：WireMock proxy/mock/reset與mapping/log；Microcks三個operation各一個sample、JS/PROXY_FALLBACK編輯器、Save成功；Sandbox合法/非法延遲、新ID、實際提交與兩種journal。三張截圖保留；初次JS失敗仍在同份證據。 |
| V01 | 完整solution build成功；受影響component實際測試如上。沒有把不同revision的分批執行合併宣稱為一次全新full regression。 |
| V02 | 實際Sol/Luna/high分工、首次結果、review／修復與限制皆記錄；沒有以不同任務難度做模型排名，沒有估算token／cost冒充測量。 |

## 重現與限制

啟動、操作 UI、API 範例和可執行驗證命令見 [操作手冊](../../operations/procurement-supplier-lab.md)。這是 localhost 的單品採購實驗，管理頁不含正式認證。WireMock頁由本專案提供；Microcks使用原生UI。PostgreSQL資料保留在 volumes；Microcks uber 的內建 Mongo 在此部署不具跨重建持久化承諾，重啟／重建後依說明重新匯入。WireMock mapping與Sandbox延遲為暫時控制，重啟套用預設。

最終保留兩個引擎 hybrid、Sandbox延遲0、供審查的資料及運行服務。受保護 `ai-collaboration-observability` 九個容器的name/ID/startedAt/status與操作前完全一致，見 observability-comparison.json。Microcks原生UI曾記錄一個未能歸因的generic `ERROR y_` console訊息；本次操作與HTTP皆成功，不宣稱其console無錯誤，也沒有執行Microcks本身另一套Conformance Test功能。已知四個EF/Wolverine sample external skips不在此次選定採購驗收範圍，未改列通過。

Framework selected checks沿用已安裝且未變更的 candidate綁定與原pilot Git range；本次product commits另由target Git validator檢查。這兩類檢查不代表新product tree取得framework獨立admission，也不代替上述runtime證據。一次未提交的 `.dev/ARCHITECTURE.md` 索引更新觸發 pinned bytes 檢查失敗，coordinator撤回自己這項更新，沒有重寫pin。既有該文件及 `.dev/project-config.yaml` inventory早於本次新增領域；本次source、solution、Compose、[workflow架構](architecture.md)及操作手冊是新增領域的現況依據。框架固定的舊索引更新留待其治理流程，不阻礙本次實作與指定驗收。

額外執行的 legacy `validate-workflow-artifacts.py` 仍回報失敗：它硬編碼 index entrypoint 必須在 discovery folder，而当前 package 明確選擇 `.dev/workflows-v2`。索引保留可實際解析的正確連結，沒有改成不存在的路徑來滿足舊檢查；沒有修改舊工具／框架pin。此相容性限制不宣稱通過，原始診斷見 legacy-locator-check.txt。選定的新版record由orchestrator工具完成schema及狀態驗證，locator的實際路徑另行核對。

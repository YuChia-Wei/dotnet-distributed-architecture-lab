# 採購與供應商整合實驗需求

Status: authorized implementation baseline; final owner review pending.
Owner: repository owner. Workflow: 2026-09-26-procurement-supplier-lab. Issue: #17.

## 來源與目標

2026-09-26 使用者採納對話中的採購入庫方向，明確要求 SupplierSandbox.WebApi、Microcks／WireMock.Net 的 mock 與真實上游 proxy 驗證、可操作的 UI 或設定說明，以及完整需求、規格、實作與 coordinator review。實作使用 GPT-6 Sol／Luna 子代理，所有工作保留在同一 workflow，最後由使用者審核。GitHub Issue 發布另獲當次明確授權。

此版本是一張採購單一項商品的實驗；供應商先支援一個 sandbox，具三個連線 profile：direct、wiremock、microcks。這是 coordinator 在使用者授權範圍內選定的初版設計，不代表完整商用採購制度。

## User stories 與驗收

| ID | User story | 可觀察驗收 |
| --- | --- | --- |
| US01 / AC01 | 採購人員希望查詢供應商商品報價並下採購單，以補充既有產品庫存。 | 能選擇既有 ProductId、供應商 SKU、數量與價格快照；取得持久化採購單及供應商接單結果。 |
| US02 / AC01 | 採購人員遇到逾時後希望查明供應商是否已接單，避免重複下單。 | 相同 clientRequestId 與相同 payload 只產生一張供應商訂單；不同 payload 回傳 409；未知結果可查單恢復。 |
| US03 / AC02 | 收貨人員希望分批登錄實際收到的貨品。 | 採購 10 件可依不同 ReceiptId 收 6、4 件；超收、零／負數及未接受的採購單均拒絕。 |
| US04 / AC02 | 庫存人員希望訊息重送時不重複入庫。 | 同一 ReceiptId 的相同收貨重播不加庫存、不再建立事件；同 ID 不同內容明確衝突；收貨和 outbox 同交易。 |
| US05 / AC03 | 開發者希望切換 mock、proxy、混合模式，比較兩套工具。 | 兩套工具各自實際證明 mock 不打上游、proxy 會打上游、混合模式依範例／mapping 判定；保留 request 與 origin 證據。 |
| US06 / AC04 | 開發者希望透過 UI 檢視與操作整合設定。 | Microcks 原生 UI 可用；WireMock.Net 本機控制頁可切模式、查看 mapping 與 request log；文件說明修改檔案及重啟後狀態。 |
| US07 / AC05 | 維護者希望從規格重現驗證結果。 | API、狀態、例外、GWT 測試與實際 HTTP／PostgreSQL／Kafka 證據可相互追溯；跳過不是通過。 |
| US08 / AC06 | 使用者希望評估模型在完整規格下的實作能力。 | 保存模型、推理設定、輸入規格、責任範圍、首輪驗證、review 發現、修復與最終狀態；不以不同任务難度推斷公平排名。 |

## 業務規則

- BR01: 採購單以本地 PurchaseOrderId 識別；clientRequestId 是建立／送單的全域冪等鍵，provider、ProductId、SKU、數量、單價、幣別皆屬不可變 identity payload。
- BR02: 數量必須為正整數；價格為非負 decimal；幣別固定初版 TWD；Guid 不可為空；SKU 為 1–64 字元，限英數、連字號與底線。
- BR03: 供應商接受／出貨不等於實際收貨，不會增加本地庫存。
- BR04: 只有 Accepted、PartiallyReceived 可新增實際收貨；同一收貨的相同重播允許在 Received 狀態回傳既存結果。已收總量不得超過訂購量。
- BR05: ReceiptId 全域唯一且綁定 PurchaseOrderId、ProductId、Quantity；兩邊都須防重，並以同一 receipt identity 投遞。
- BR06: 任何未能確定的外部結果保存 SubmissionUnknown，可透過查詢供應商原 clientRequestId 恢復；不可把 transport failure 解讀為供應商拒絕。
- BR07: 庫存端遇到尚未初始化的 ProductId 保留失敗／可重試狀態，不擅自建立商品或庫存。測試先建立既有 ProductId 及初始庫存。

## 範圍與限制

包含查報價、單品採購、送單／查單、實際收貨、持久化與非同步入庫、兩個模擬平台及管理控制、Docker profile 與重現說明。不包含金流、退款、供應商主檔 CRUD、多幣別、多行訂單、審批／稅務／會計、正式認證與正式部署。管理入口仅供 localhost 實驗，避免把未驗證的本機管理端點發布至外網。

不改變 Products／Orders 的 Dapper 或 Inventory 的 EF Core 選擇。新增 Procurement 選擇 Dapper＋PostgreSQL，Supplier sandbox 選擇自己的 PostgreSQL storage。既有資料與 volumes 必須保留。

## Source bindings

- 本對話兩次使用者需求與 Issue #17：需求／執行授權；最後 owner review 尚未發生。
- `.dev/ARCHITECTURE.md`、現有 Inventory receipt 類比來源 reservation adapter：觀察到的現況，非新增能力證據。
- `architecture.md`、`specifications.md`、`test-specification.md`：本 workflow 選定實作契約與驗證預期。

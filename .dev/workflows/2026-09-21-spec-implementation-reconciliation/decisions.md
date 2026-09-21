# 規格與實作差異處理紀錄

基準版本：`2ee6ee21cfe64da4b87b8c57b5a661b9b9a8f517`。
授權：2026-09-21 使用者要求修復 review 差異，以較新的版本為主，仍無法判斷者集中決策。

「較新」以具體行為、契約或已核准決策的變更為準；整份文件的後續格式修改與保留原行為的 ORM 改寫，不視為另一次業務決策。同一提交內矛盾，依重建入口既有的 requirement/ADR、production spec、problem frame、test spec 優先序處理。

## 已可判定

| ID | 差異 | 時序與依據 | 處理 |
| --- | --- | --- | --- |
| R01 | Orders outbox 重試改寫 OccurredOn | 保留時間規格於 `3a5fbb3`（2026-08-26）加入，晚於 `8f9ff26`（2026-07-14）的 relay 及事件建構子 | 修正程式反序列化，保留既有 producer 呼叫與 wire fields；測試四種事件與 relay retry |
| R03 | 寫入端一律 Dapper 的需求與 Inventory EF Core 衝突 | 2026-09-21 owner 決定與 `cc25513` 的 Inventory EF Core 實作較新 | 更新 requirements、持久化 spec，Products/Orders 仍用 Dapper |
| R04 | GetOrderDetails 測試規格要求額外欄位與 typed failure | production spec、ORD-007 與矛盾 test spec 同於 `3a5fbb3`；正式契約優先 | 保留 OrderId、單一 ProductId/Quantity line 與 null-to-404；修 test spec 與失效 requirement refs |
| R05 | Orders outbox 成功後設定 DeliveredAt 或刪除 | 同一 `3a5fbb3` 中 persistence contract 明定 delete，測試規格誤寫 DeliveredAt | 修測試規格為發布成功後刪除；不導入新欄位或改 retention |
| R06 | 套件與重建專案清單落後 | `81a2936`（2026-09-12）更新套件/diagnostics，`ed27f6b`（2026-09-17）加入 sample，`cc25513` 更新 Inventory | 依目前 csproj、solution、Compose 更新套件與 22 product + 3 sample + 6 test = 31 的清單及依賴；刷新 inventory provenance |
| R08 | Inventory 併發/rollback/commerce 仍標記未驗證 | 保留的 `edd18d7` 執行記錄於 2026-09-21 通過 122 tests，零失敗/跳過 | 更新 active coverage/status，明示證據日期與 subject；不改歷史報告，也不當成本次修復的 fresh test |
| R09 | 所有 Consumer 均無 handler、Products route 無 producer | `81a2936` 已加入 Orders diagnostics handler 與 Product diagnostics publisher | 區分診斷範例和仍未定義的 business reactions，不宣稱 business gaps 已完成 |
| R10 | Inventory retention 同時被描述為實作與 deferred | `6ad447c`（2026-08-27）已加入 RetainAll/PublishedForDays | 保留實作說明；deferred 僅指未實作的 archive/export policy |
| R11 | 部分測試狀態、requirement ID 與工具清單過時 | 以目前測試內容、現存 requirement ID、已退役 tools 的目標決策為依據 | 僅更新實際覆蓋範圍與可解析的追溯；未執行/未實作項目繼續保留 |

## 已決策 R02：Inventory 清理後重播

狀態：2026-09-21 owner 回覆「套用建議」，核准選項 A。

`07aeea9`（2026-08-27 08:59 +08）建立成功重播不新增 outbox 的保證；`6ad447c`（09:44 +08）新增有限期清理，同時保留原保證及依現有 row 防重的程式。`cc25513` 的 EF 改寫明示保留原行為，沒有決定清理後重播的語意。故不能僅憑較新的 EF 修改日期撤回原契約。

- A（建議）：回傳既有預留結果，不再建立發布意圖。仍不保證 broker exactly-once；手動刪除或舊資料缺失須由明確復原流程處理。
- B：維持程式目前可重新入列的行為，明示防重範圍受 outbox retention 限制。庫存不再扣，但歷史事件可能以同一 MessageId 再發布，重建時的 metadata 也可能不同。

必要驗證：真 PostgreSQL 完成 reserve、publish、age PublishedAt、有限期清理，再重播同一 operation；確認 stock、operation、outbox 與 publisher 結果。這個資料庫邊界不需要 Kafka。

## 已決策 R07：PlaceOrder domain event 欄位

狀態：2026-09-21 owner 回覆「套用建議」，核准選項 A。

CBF 的 `Id`/`Status` 清單於 `9f3ddff`（2026-04-23）加入，後續回復與其他修改沒有重定義欄位。實作既有 `OrderId`、`OccurredOn`、`EventId`，沒有 `Status`。若它是較新的正式欄位契約，實作變更會影響已儲存的 event stream；若它是來源還原文件的抄寫錯誤，應修文件。較新的 ORD-002/ORD-006、production specs 與 persistence envelope 都沒有明定這個 domain event payload；integration event schema 也不能代替 domain event 契約，因此交由 owner 裁決；owner 現已選擇保留程式格式並修正 CBF。

- A（建議）：採現有程式 schema，將 CBF 的 domain_events.attributes 修為 OrderId、保留 OccurredOn/EventId、移除 Status，維持現有事件的序列化與重播。aggregate 的 semantic_tags Id/Status 不受影響。
- B：採較新 CBF 的欄位意圖，調整 domain event 程式，先制定既存事件 JSON 的相容與遷移方式；不能僅改欄位後直接套用到既存資料。

兩項建議均已獲明確授權。R02 實作為首次成功才呼叫訊息 factory 並 staging；重播只回傳持久化結果，即使原 row 已清理也不重建。R07 修正文件，既存 domain event 格式不變。

## 刻意保留的未完成範圍

- Products 仍使用 legacy broker 設定，統一 Messaging:* 是已記錄的 reconstruction quality uplift。
- 明確 HTTP validation/not-found/concurrency error mapping、部分直接 use-case 測試、Products/Orders 真資料庫 rollback coverage 等仍依原文件狀態處理。
- 業務 consumer ownership、Kafka + RabbitMQ dual broadcast 與兩次獨立 clean-room reconstruction 仍未完成。
- 本工作不提供 whole-system 100% spec-compliance 或新的 framework adoption 結論。

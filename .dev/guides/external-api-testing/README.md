# 外部 API 測試實驗室

本指南供團隊在既有的商務前台與採購實驗室中，選擇供應商替身、觀察真正的上游呼叫，並說明採購到收貨及銷售保留的邊界。對應 [Issue #20](https://github.com/YuChia-Wei/dotnet-distributed-architecture-lab/issues/20)。本文描述目前追蹤於 repository 的實作；畫面與 HTTP 結果仍以當次啟動後的服務讀回為準。

| 想解決的問題 | 閱讀 |
| --- | --- |
| 兩套工具能做什麼、目前操作頁能做什麼、何時選哪一套 | [方案比較](solution-comparison.md) |
| 入口、控制面、資料面、資料庫與訊息拓樸 | [架構](architecture.md) |
| 模擬、代理、未知送單、收貨與銷售的呼叫順序 | [時序圖](sequences.md) |
| 從啟動、切換到可重現演示的操作與觀察點 | [展示指南](demo-guide.md) |
| 程式、設定、原廠文件與結論依據 | [來源](sources.md) |

實驗室固定在 localhost。業務前台是 `http://127.0.0.1:8888/web/`，管理後台是 `http://127.0.0.1:8888/admin/`。WireMock.Net 的資料端點在 8183，repository 自製控制頁在 8182；Microcks 原生 UI 在 8184。`ISupplierGateway` 的 `direct`、`wiremock`、`microcks` 是固定供應商路徑，同一筆採購的 provider 不會因操作員切換 mock 模式而改寫。這些入口沒有部署級身分驗證，僅供本機實驗。

先看 [採購實驗操作手冊](../../operations/procurement-supplier-lab.md) 與 [前台操作手冊](../../operations/commerce-frontend.md) 的實際啟動條件；本指南補足團隊選型、圖解與展示判讀，不取代既有資料庫初始化和驗收步驟。`mock`、`proxy`、`hybrid` 皆是執行期預設。WireMock 重啟回到設定的啟動模式；Microcks uber 的內部資料不應視為持久資產，重啟後須檢查並重匯入。演示後請讀回狀態，再決定下一個情境。

## 團隊分享檔案

- [簡報與講者筆記](../../presentations/external-api-testing/README.md)：可編輯 PowerPoint、PDF 閱讀版與逐頁講稿。
- [8 張圖的圖檔索引](diagrams/README.md)：SVG、PNG 與 Mermaid 原始碼，可引用到團隊文件。
- [離線圖庫](diagrams/index.html)：瀏覽器開啟即可逐張查看。

# 外部 API 測試團隊簡報

此目錄提供約 20 分鐘的繁體中文團隊導覽。[PPTX](external-api-testing.pptx) 是可編輯的 17 張簡報，架構與時序圖使用原生投影片物件；[PDF](external-api-testing.pdf) 是由逐張 180 dpi 預覽組成的閱讀副本。PDF 文字為影像，請用 PPTX 編輯內容，或閱讀可搜尋的 [講者與示範筆記](speaker-notes.md)。

內容以既有 WireMock.Net、Microcks、Supplier Sandbox、Procurement 與 Inventory 實驗為準。模擬、透傳與混合模式的證據，需同時讀回有效模式、回應 `origin` 與 Sandbox request log。接受採購單不增加庫存；實際收貨才會透過 source outbox、Kafka 與 Inventory 的 ReceiptId 去重使庫存增加。歷史文件與本簡報不代表 2026-09-28 當次服務已啟動或驗收通過。

使用順序：先閱讀 [操作與來源文件](../../operations/procurement-supplier-lab.md) 及 [前後台操作手冊](../../operations/commerce-frontend.md)，再按 [講者與示範筆記](speaker-notes.md) 準備商品、服務與測試識別。詳細架構、時序與方案比較在 [團隊指南](../../guides/external-api-testing/README.md)。

`build-deck.mjs` 使用 `@oai/artifact-tool` 與內建 presentation finalizer。執行環境需提供絕對路徑 `SKILL_DIR`、`RUNTIME_PYTHON`、`RUNTIME_NODE_MODULES`、`RUNTIME_NODE`、`RUNTIME_BIN_DIR`，以及與 source 同目錄的 runtime `node_modules` 連結。這些路徑由 Codex `load_workspace_dependencies` 與已安裝 Presentations skill 提供。每次執行都產生帶時間戳的 `output/*.pptx` 與私有 `.build` 驗證收據；檢視後再將選定檔案命名為發布用的 `external-api-testing.pptx`。PDF 由已驗證 PPTX 的每張投影片渲染而成。

# Cross-Domain Test Specs

本目錄放置跨 bounded context 的測試規格。

適合放這裡的內容：

- Order 與 Inventory 之間的協作流程
- 多個 domain 共同參與的 MQ flow
- eventual consistency 驗證路徑
- compensation / retry / duplicate delivery 相關 scenario

不適合放這裡的內容：

- 單一 domain 內可完整描述的 aggregate 或 use case 測試
- 純 UI journey，若重點是完整旅程請放 `../e2e/`

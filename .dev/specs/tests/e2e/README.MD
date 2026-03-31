# E2E Test Specs

本目錄放置端對端旅程的測試規格。

適合放這裡的內容：

- 從 API 或 UI 入口開始的完整業務旅程
- 涵蓋多層 adapter、application、messaging、persistence 的驗證
- 使用者可觀察結果優先的 scenario

不適合放這裡的內容：

- 單一 use case handler 的測試意圖
- 單一 aggregate invariant 驗證
- 僅針對 repository 或 MQ contract 的 integration 驗證

# Profile-Based Testing Rationale

## Decision Pattern

測試需支援多種 profile，例如：

- InMemory
- Outbox / PostgreSQL integration

且 profile 選擇不應硬寫在 base test class。

## Why

### 1. 同一測試應能驗證不同實作策略

如果 command side 同時支援 in-memory 與 outbox，測試不應只綁死一種環境。

### 2. 環境選擇屬於 runtime concern

測試執行用哪個 profile，本質上是配置問題，而不是測試類別繼承結構的一部分。

### 3. 避免 BaseTestClass 變成隱性全域狀態

把環境選擇寫在 base class 會：

- 增加隱藏耦合
- 讓測試切換模式變困難
- 讓 CI / local / integration 行為不一致

## Why Not

### Base Test Class 內硬編碼環境

缺點：

- 無法清楚從執行命令看出目前測的是哪個 profile
- 測試基底類過度強勢
- 難以維護與擴展

## Practical Rule

- profile 由環境變數與 `appsettings.{Environment}.json` 決定
- 測試本體不負責偷偷設定全域執行環境
- 同一套測試應能在多個 profile 下重跑

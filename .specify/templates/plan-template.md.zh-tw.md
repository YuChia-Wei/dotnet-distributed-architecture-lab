# 實作計畫：[功能]

**分支**：`[###-feature-name]` | **日期**：[日期] | **規格**：[連結]
**輸入**：來自 `/specs/[###-feature-name]/spec.md` 的功能規格

**注意**：此範本由 `/speckit.plan` 命令填寫。執行流程請參閱 `.specify/templates/commands/plan.md`。

## 摘要

[從功能規格中提取：主要需求 + 來自研究的技術方法]

## 技術背景

<!--
  需要執行：將此部分的內容替換為專案的技術細節。
  此處的結構僅為建議，用以引導迭代過程。
-->

**語言/版本**：[例如，Python 3.11, Swift 5.9, Rust 1.75 或需要釐清]  
**主要相依套件**：[例如，FastAPI, UIKit, LLVM 或需要釐清]  
**儲存**：[如果適用，例如 PostgreSQL, CoreData, 檔案或不適用]  
**測試**：[例如，pytest, XCTest, cargo test 或需要釐清]  
**目標平台**：[例如，Linux 伺服器, iOS 15+, WASM 或需要釐清]
**專案類型**：[單一/網站/行動應用 - 決定原始碼結構]  
**效能目標**：[領域特定，例如 1000 req/s, 10k lines/sec, 60 fps 或需要釐清]  
**限制**：[領域特定，例如 <200ms p95, <100MB 記憶體, 可離線使用或需要釐清]  
**規模/範圍**：[領域特定，例如 1 萬使用者, 1 百萬行程式碼, 50 個畫面或需要釐清]

## 原則檢查

*閘門：必須在第 0 階段研究前通過。在第 1 階段設計後重新檢查。*

[閘門根據原則檔案決定]

## 專案結構

### 文件 (此功能)

```text
specs/[###-feature]/
├── plan.md              # 此檔案 (/speckit.plan 命令輸出)
├── research.md          # 第 0 階段輸出 (/speckit.plan 命令)
├── data-model.md        # 第 1 階段輸出 (/speckit.plan 命令)
├── quickstart.md        # 第 1 階段輸出 (/speckit.plan 命令)
├── contracts/           # 第 1 階段輸出 (/speckit.plan 命令)
└── tasks.md             # 第 2 階段輸出 (/speckit.tasks 命令 - 並非由 /speckit.plan 建立)
```

### 原始碼 (儲存庫根目錄)
<!--
  需要執行：將下方的預留位置樹狀結構替換為此功能的具體佈局。
  刪除未使用的選項，並使用真實路徑擴充所選結構 (例如，apps/admin, packages/something)。
  交付的計畫不得包含選項標籤。
-->

```text
# [若未使用則移除] 選項 1：單一專案 (預設)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [若未使用則移除] 選項 2：Web 應用程式 (偵測到 "frontend" + "backend" 時)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [若未使用則移除] 選項 3：行動應用 + API (偵測到 "iOS/Android" 時)
api/
└── [同上方的 backend]

ios/ 或 android/
└── [平台特定結構：功能模組、UI 流程、平台測試]
```

**結構決策**：[記錄所選結構並參考上方擷取的真實目錄]

## 複雜度追蹤

> **僅在「原則檢查」有必須說明的違規時填寫**

| 違規 | 為何需要 | 為何拒絕更簡單的替代方案 |
|-----------|------------|-------------------------------------|
| [例如，第 4 個專案] | [目前需求] | [為何 3 個專案不足] |
| [例如，儲存庫模式] | [特定問題] | [為何直接存取資料庫不足] |
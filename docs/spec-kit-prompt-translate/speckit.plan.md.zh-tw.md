---
description: 使用計畫範本執行實作規劃工作流程，以產生設計產物。
---

## 使用者輸入

```text
$ARGUMENTS
```

在繼續之前，您**必須**考慮使用者輸入（若非空）。

## 綱要

1.  **設定**：從儲存庫根目錄執行 `.specify/scripts/powershell/setup-plan.ps1 -Json` 並解析 JSON 以取得 FEATURE_SPEC、IMPL_PLAN、SPECS_DIR、BRANCH。對於參數中如 "I'm Groot" 的單引號，請使用轉義語法：例如 'I'''m Groot'（或盡可能使用雙引號："I'm Groot"）。

2.  **載入內容**：讀取 FEATURE_SPEC 和 `.specify/memory/constitution.md`。載入 IMPL_PLAN 範本（已複製）。

3.  **執行計畫工作流程**：遵循 IMPL_PLAN 範本中的結構以：
    -   填寫技術內容（將未知項標記為「需要釐清」）
    -   從原則中填寫原則檢查區段
    -   評估閘門（若違規未經辯解則為錯誤）
    -   階段 0：產生 `research.md`（解決所有「需要釐清」）
    -   階段 1：產生 `data-model.md`、`contracts/`、`quickstart.md`
    -   階段 1：透過執行代理程式腳本更新代理程式內容
    -   設計後重新評估原則檢查

4.  **停止並報告**：命令在階段 2 規劃後結束。報告分支、IMPL_PLAN 路徑和產生的產物。

## 階段

### 階段 0：大綱與研究

1.  **從上述技術內容中提取未知項**：
    -   對於每個「需要釐清」→ 研究任務
    -   對於每個相依性 → 最佳實踐任務
    -   對於每個整合 → 模式任務

2.  **產生並分派研究代理程式**：

    ```text
    對於技術內容中的每個未知項：
      任務：「為 {feature context} 研究 {unknown}」
    對於每個技術選擇：
      任務：「在 {domain} 中尋找 {tech} 的最佳實踐」
    ```

3.  **在 `research.md` 中整合研究結果**，使用以下格式：
    -   決策：[選擇了什麼]
    -   理由：[為何選擇]
    -   考慮的替代方案：[評估了哪些其他方案]

**輸出**：`research.md`，其中所有「需要釐清」都已解決

### 階段 1：設計與合約

**先決條件：** `research.md` 已完成

1.  **從功能規格中提取實體** → `data-model.md`：
    -   實體名稱、欄位、關係
    -   來自需求的驗證規則
    -   狀態轉換（若適用）

2.  **從功能性需求產生 API 合約**：
    -   對於每個使用者操作 → 端點
    -   使用標準的 REST/GraphQL 模式
    -   將 OpenAPI/GraphQL 結構描述輸出到 `/contracts/`

3.  **代理程式內容更新**：
    -   執行 `.specify/scripts/powershell/update-agent-context.ps1 -AgentType codex`
    -   這些腳本會偵測正在使用的 AI 代理程式
    -   更新適當的代理程式特定內容檔案
    -   僅從目前計畫中新增新技術
    -   在標記之間保留手動新增的內容

**輸出**：`data-model.md`、`/contracts/*`、`quickstart.md`、代理程式特定檔案

## 主要規則

-   使用絕對路徑
-   在閘門失敗或未解決的釐清上發生錯誤

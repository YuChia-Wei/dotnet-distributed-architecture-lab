---
description: 透過處理並執行 tasks.md 中定義的所有任務來執行實作計畫。
---

## 使用者輸入

```text
$ARGUMENTS
```

在繼續之前，您**必須**考慮使用者輸入（若非空）。

## 綱要

1.  從儲存庫根目錄執行 `.specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks` 並解析 FEATURE_DIR 和 AVAILABLE_DOCS 列表。所有路徑必須是絕對路徑。對於參數中如 "I'm Groot" 的單引號，請使用轉義語法：例如 'I'''m Groot'（或盡可能使用雙引號："I'm Groot"）。

2.  **檢查清單狀態**（如果 `FEATURE_DIR/checklists/` 存在）：
    -   掃描 `checklists/` 目錄中的所有清單檔案
    -   對於每個清單，計算：
        -   總項目數：所有符合 `- [ ]` 或 `- [X]` 或 `- [x]` 的行
        -   已完成項目數：符合 `- [X]` 或 `- [x]` 的行
        -   未完成項目數：符合 `- [ ]` 的行
    -   建立一個狀態表：

        ```text
        | 清單 | 總計 | 已完成 | 未完成 | 狀態 |
        |-----------|-------|-----------|------------|--------|
        | ux.md     | 12    | 12        | 0          | ✓ 通過 |
        | test.md   | 8     | 5         | 3          | ✗ 失敗 |
        | security.md | 6   | 6         | 0          | ✓ 通過 |
        ```

    -   計算總體狀態：
        -   **通過**：所有清單都沒有未完成的項目
        -   **失敗**：一個或多個清單有未完成的項目

    -   **如果任何清單未完成**：
        -   顯示包含未完成項目計數的表格
        -   **停止**並詢問：「有些清單未完成。您確定要繼續實作嗎？（是/否）」
        -   在繼續之前等待使用者回應
        -   如果使用者說「否」或「等待」或「停止」，則中止執行
        -   如果使用者說「是」或「繼續」，則繼續執行步驟 3

    -   **如果所有清單都已完成**：
        -   顯示顯示所有清單都通過的表格
        -   自動繼續執行步驟 3

3.  載入並分析實作內容：
    -   **必要**：讀取 `tasks.md` 以取得完整的任務列表和執行計畫
    -   **必要**：讀取 `plan.md` 以取得技術棧、架構和檔案結構
    -   **若存在**：讀取 `data-model.md` 以取得實體和關係
    -   **若存在**：讀取 `contracts/` 以取得 API 規格和測試需求
    -   **若存在**：讀取 `research.md` 以取得技術決策和限制
    -   **若存在**：讀取 `quickstart.md` 以取得整合情境

4.  **專案設定驗證**：
    -   **必要**：根據實際專案設定建立/驗證忽略檔案：

    **偵測與建立邏輯**：
    -   檢查以下命令是否成功，以確定儲存庫是否為 git 儲存庫（若是，則建立/驗證 `.gitignore`）：

        ```sh
        git rev-parse --git-dir 2>/dev/null
        ```

    -   檢查 `Dockerfile*` 是否存在或 `plan.md` 中是否有 Docker → 建立/驗證 `.dockerignore`
    -   檢查 `.eslintrc*` 或 `eslint.config.*` 是否存在 → 建立/驗證 `.eslintignore`
    -   檢查 `.prettierrc*` 是否存在 → 建立/驗證 `.prettierignore`
    -   檢查 `.npmrc` 或 `package.json` 是否存在 → 建立/驗證 `.npmignore`（如果發布）
    -   檢查 terraform 檔案（`*.tf`）是否存在 → 建立/驗證 `.terraformignore`
    -   檢查是否需要 `.helmignore`（存在 helm charts）→ 建立/驗證 `.helmignore`

    **如果忽略檔案已存在**：驗證它是否包含必要的模式，僅附加缺失的關鍵模式
    **如果忽略檔案缺失**：使用偵測到的技術的完整模式集建立

    **按技術分類的常見模式**（來自 `plan.md` 技術棧）：
    -   **Node.js/JavaScript/TypeScript**：`node_modules/`, `dist/`, `build/`, `*.log`, `.env*`
    -   **Python**：`__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `dist/`, `*.egg-info/`
    -   **Java**：`target/`, `*.class`, `*.jar`, `.gradle/`, `build/`
    -   **C#/.NET**：`bin/`, `obj/`, `*.user`, `*.suo`, `packages/`
    -   **Go**：`*.exe`, `*.test`, `vendor/`, `*.out`
    -   **Ruby**：`.bundle/`, `log/`, `tmp/`, `*.gem`, `vendor/bundle/`
    -   **PHP**：`vendor/`, `*.log`, `*.cache`, `*.env`
    -   **Rust**：`target/`, `debug/`, `release/`, `*.rs.bk`, `*.rlib`, `*.prof*`, `.idea/`, `*.log`, `.env*`
    -   **Kotlin**：`build/`, `out/`, `.gradle/`, `.idea/`, `*.class`, `*.jar`, `*.iml`, `*.log`, `.env*`
    -   **C++**：`build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.so`, `*.a`, `*.exe`, `*.dll`, `.idea/`, `*.log`, `.env*`
    -   **C**：`build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.a`, `*.so`, `*.exe`, `Makefile`, `config.log`, `.idea/`, `*.log`, `.env*`
    -   **Swift**：`.build/`, `DerivedData/`, `*.swiftpm/`, `Packages/`
    -   **R**：`.Rproj.user/`, `.Rhistory`, `.RData`, `.Ruserdata`, `*.Rproj`, `packrat/`, `renv/`
    -   **通用**：`.DS_Store`, `Thumbs.db`, `*.tmp`, `*.swp`, `.vscode/`, `.idea/`

    **工具特定模式**：
    -   **Docker**：`node_modules/`, `.git/`, `Dockerfile*`, `.dockerignore`, `*.log*`, `.env*`, `coverage/`
    -   **ESLint**：`node_modules/`, `dist/`, `build/`, `coverage/`, `*.min.js`
    -   **Prettier**：`node_modules/`, `dist/`, `build/`, `coverage/`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
    -   **Terraform**：`.terraform/`, `*.tfstate*`, `*.tfvars`, `.terraform.lock.hcl`
    -   **Kubernetes/k8s**：`*.secret.yaml`, `secrets/`, `.kube/`, `kubeconfig*`, `*.key`, `*.crt`

5.  解析 `tasks.md` 結構並提取：
    -   **任務階段**：設定、測試、核心、整合、潤飾
    -   **任務相依性**：循序與並行執行規則
    -   **任務細節**：ID、描述、檔案路徑、並行標記 [P]
    -   **執行流程**：順序和相依性需求

6.  遵循任務計畫執行實作：
    -   **分階段執行**：在移至下一個階段之前完成每個階段
    -   **尊重相依性**：按順序執行循序任務，並行任務 [P] 可以一起執行
    -   **遵循 TDD 方法**：在對應的實作任務之前執行測試任務
    -   **基於檔案的協調**：影響相同檔案的任務必須循序執行
    -   **驗證檢查點**：在繼續之前驗證每個階段的完成情況

7.  實作執行規則：
    -   **首先設定**：初始化專案結構、相依性、組態
    -   **測試先於程式碼**：如果您需要為合約、實體和整合情境撰寫測試
    -   **核心開發**：實作模型、服務、CLI 命令、端點
    -   **整合工作**：資料庫連線、中介軟體、日誌記錄、外部服務
    -   **潤飾和驗證**：單元測試、效能優化、文件

8.  進度追蹤和錯誤處理：
    -   在每個完成的任務後報告進度
    -   如果任何非並行任務失敗，則中止執行
    -   對於並行任務 [P]，繼續執行成功的任務，報告失敗的任務
    -   提供清晰的錯誤訊息和上下文以進行偵錯
    -   如果無法繼續實作，則建議後續步驟
    -   **重要** 對於已完成的任務，請務必在任務檔案中將任務標記為 [X]。

9.  完成驗證：
    -   驗證所有必要的任務都已完成
    -   檢查實作的功能是否符合原始規格
    -   驗證測試是否通過且覆蓋率符合需求
    -   確認實作遵循技術計畫
    -   報告最終狀態並總結已完成的工作

注意：此命令假設 `tasks.md` 中存在完整的任務分解。如果任務不完整或缺失，建議先執行 `/speckit.tasks` 以重新產生任務列表。

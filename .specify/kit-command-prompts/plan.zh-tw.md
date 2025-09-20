---
description: 使用計畫範本執行實作規劃工作流程，以產出設計產物。
---

根據作為引數提供的實作細節，執行以下操作：

1. 從儲存庫根目錄執行 `.specify/scripts/powershell/setup-plan.ps1 -Json`，並解析 FEATURE_SPEC、IMPL_PLAN、SPECS_DIR、BRANCH 的 JSON。所有未來的檔案路徑都必須是絕對路徑。
2. 讀取並分析功能規格以了解：
   - 功能需求和使用者故事
   - 功能性和非功能性需求
   - 成功標準和驗收標準
   - 任何提及的技術限制或相依性

3. 讀取位於 `.specify/memory/constitution.md` 的章程以了解章程要求。

4. 執行實作計畫範本：
   - 載入 `.specify/templates/plan-template.md`（已複製到 IMPL_PLAN 路徑）
   - 將輸入路徑設定為 FEATURE_SPEC
   - 執行執行流程（主要）函式步驟 1-9
   - 該範本是獨立且可執行的
   - 遵循指定的錯誤處理和閘道檢查
   - 讓範本引導在 $SPECS_DIR 中產出產物：
     * 階段 0 產出 research.md
     * 階段 1 產出 data-model.md、contracts/、quickstart.md
     * 階段 2 產出 tasks.md
   - 將使用者從引數提供的細節整合到技術情境中：$ARGUMENTS
   - 在完成每個階段時更新進度追蹤

5. 驗證執行是否完成：
   - 檢查進度追蹤是否顯示所有階段皆已完成
   - 確保所有必要的產物都已產出
   - 確認執行中沒有錯誤狀態

6. 報告結果，包含分支名稱、檔案路徑和產出的產物。

對所有檔案操作使用相對於儲存庫根目錄的絕對路徑，以避免路徑問題。
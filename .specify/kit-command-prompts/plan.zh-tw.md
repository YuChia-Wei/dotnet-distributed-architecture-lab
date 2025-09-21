---
description: 使用計劃模板執行實施規劃工作流程以生成設計產出。
---

使用者輸入可以直接由代理程式提供，或在 `$ARGUMENTS` 中提供 - 在繼續處理提示之前，您 **必須** 考慮它（如果非空）。

使用者輸入：

$ARGUMENTS

鑑於作為參數提供的實施細節，請執行以下操作：

1. 從 repo 根目錄執行 `.specify/scripts/powershell/setup-plan.ps1 -Json` 並解析 FEATURE_SPEC、IMPL_PLAN、SPECS_DIR、BRANCH 的 JSON。所有未來的檔案路徑都必須是絕對路徑。
2. 閱讀並分析功能規格以了解：
   - 功能需求和使用者故事
   - 功能性和非功能性需求
   - 成功標準和驗收標準
   - 任何提及的技術限制或依賴關係

3. 閱讀 `.specify/memory/constitution.md` 中的章程以了解章程要求。

4. 執行實施計劃模板：
   - 載入 `.specify/templates/plan-template.md`（已複製到 IMPL_PLAN 路徑）
   - 將輸入路徑設定為 FEATURE_SPEC
   - 執行執行流程（主要）函式步驟 1-9
   - 該模板是獨立且可執行的
   - 遵循指定的錯誤處理和閘道檢查
   - 讓模板引導在 $SPECS_DIR 中產生交付項目：
     * 階段 0 產生 research.md
     * 階段 1 產生 data-model.md、contracts/、quickstart.md
     * 階段 2 產生 tasks.md
   - 將使用者提供的詳細資訊從參數合併到技術背景中：$ARGUMENTS
   - 在完成每個階段時更新進度追蹤

5. 驗證執行完成：
   - 檢查進度追蹤顯示所有階段已完成
   - 確保所有必要的交付項目均已產生
   - 確認執行中沒有錯誤狀態

6. 報告結果，包括分支名稱、檔案路徑和產生的交付項目。

對所有檔案操作使用儲存庫根目錄的絕對路徑，以避免路徑問題。

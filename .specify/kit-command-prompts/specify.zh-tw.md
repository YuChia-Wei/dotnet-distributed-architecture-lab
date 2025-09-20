---
description: 從自然語言的功能描述中建立或更新功能規格。
---

根據作為引數提供的功能描述，執行以下操作：

1. 從儲存庫根目錄執行腳本 `.specify/scripts/powershell/create-new-feature.ps1 -Json "$ARGUMENTS"`，並解析其 JSON 輸出以取得 BRANCH_NAME 和 SPEC_FILE。所有檔案路徑都必須是絕對路徑。
  **重要** 您只能執行此腳本一次。JSON 會在終端機中作為輸出提供 - 請務必參考它以取得您要尋找的實際內容。
2. 載入 `.specify/templates/spec-template.md` 以了解必要的區段。
3. 使用範本結構將規格寫入 SPEC_FILE，將預留位置替換為從功能描述（引數）衍生的具體細節，同時保留區段順序和標題。
4. 報告完成情況，包含分支名稱、規格檔案路徑以及為下一階段做好準備。

注意：該腳本在寫入之前會建立並簽出新分支，並初始化規格檔案。
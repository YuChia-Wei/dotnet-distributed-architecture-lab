# PRD 分群與範本

此目錄提供「單一檔案」與「模組化分群」兩種 PRD 範本：

- templates/single-file：原本的單檔 PRD 範本（英文與繁中）。
- templates/modular/en：模組化英文範本，分拆為 Summary、Goals... 等段落。
- templates/modular/zh-TW：模組化繁中範本，分拆為 摘要、目標... 等段落。

## 使用方式（建議）

1. 選擇語系（`en` 或 `zh-TW`）。
2. 複製模組化範本整個資料夾到一個新目錄（例如：`PRD/Invoices/`）。
3. 依序填寫各段落檔案（01～06）。
4. 若需要合併為單檔，可自行以文件工具、腳本或 CI 任務串接，將各檔案依序合併。

## 命名與結構建議

- 每個 PRD 放在 `PRD/<Service or Feature>/` 目錄下（例如：`PRD/Orders/`）。
- 維持 2 語系並行時，請於 `<Feature>/en` 與 `<Feature>/zh-TW` 內分別維護。
- 以數字前綴（01～06）固定段落順序，方便檢視與自動合併。

## 段落對應（單檔 → 模組化）

- Summary → 01-summary / 01-摘要
- Goals → 02-goals / 02-目標
- Non-Goals → 03-non-goals / 03-非目標
- Constraints → 04-constraints / 04-限制
- Acceptance Criteria → 05-acceptance-criteria / 05-驗收準則
- Plan → 06-plan / 06-計畫


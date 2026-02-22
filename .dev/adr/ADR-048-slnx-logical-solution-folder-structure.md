# ADR-048: `.slnx` 採用邏輯分組方案資料夾結構

## 狀態

Accepted (2026-02-18)

## 背景

目前專案使用 `.slnx` 作為 solution 檔，Solution Folder 呈現方式為：

- `/Inventory/DomainCore/`
- `/Order/Presentation/`
- `/Product/DomainCore/`

此結構主要反映 Bounded Context 與分層語意，而非實體目錄（例如 `src/Inventory/DomainCore`）。

原先規範要求 Solution Folder（除 `tests` 外）需對應實體目錄，與現行實務不一致，造成規範與實際作法衝突。

## 決策

`.slnx` 的 Solution Folder 改採「邏輯分組」規範，允許不對應實體目錄，並固定命名風格如下：

- 一律使用前後斜線：`/{Group}/`、`/{Group}/{SubGroup}/`
- 以 BC 與層級語意分組（如：`/Order/DomainCore/`、`/Order/Presentation/`）
- 測試專案統一放在 `/tests/`

## 理由

- 提升 Solution Explorer 的語意可讀性，直接反映 BC 邊界與分層。
- 降低新成員理解成本，先看 solution 分組即可掌握架構。
- 與現行專案結構一致，避免為了符合規範而進行低價值重排。

## 取捨

### 優點

- BC/Layer 導向視圖更清楚，利於日常開發與 review。
- 方案結構穩定，不受實體路徑重構影響。
- 可在不改動檔案目錄的情況下維持高可讀性。

### 缺點

- Solution Folder 與實體路徑不一一對應，初期可能需額外熟悉。
- 目錄對應型自動檢查規則不再適用，需改為命名格式檢查。

## 實施規則

- 新增專案時，`dotnet sln ... add` 必須搭配 `--solution-folder`。
- `--solution-folder` 值必須符合前後斜線格式，例如 `"/Inventory/Presentation/"`。
- 不使用 `src` 作為 Solution Folder 的必要前綴；以語意分組優先。

## 相關

- [project-structure.md](../standards/project-structure.md)
- [quick-setup.md](../standards/quick-setup.md)

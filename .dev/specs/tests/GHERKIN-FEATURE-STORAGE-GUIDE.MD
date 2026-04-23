# Gherkin Feature Storage Guide

本文件定義本 repo 的 Gherkin `.feature` 正式存放規範。

## 1. 目的

本 repo 同時有兩種測試相關 artifact：

- `.dev/specs/tests/`
  - 測試意圖、scenario design、assertion notes、coverage gaps、追溯資訊
- `tests/Features/`
  - 正式維護、可被 IDE / BDD 工具直接使用的 Gherkin `.feature`

此分工的目標是：

- 保持 `.feature` 靠近測試程式與 step definitions，提升 IDE 整合與長期維護性
- 保持 `.dev/specs/tests/` 作為 test intent 與規格追溯區
- 避免把規格文件區誤當成測試執行資產區

## 2. 正式規範

正式 `.feature` 檔一律放在：

```text
tests/Features/
```

不要把正式 `.feature` 放在：

- `.dev/specs/tests/`
- `.dev/standards/examples/`
- 任意 domain source 專案資料夾

## 3. 目錄結構

### Domain-local

```text
tests/Features/<domain>/<use-case>.feature
```

例：

- `tests/Features/order/place-order.feature`
- `tests/Features/product/create-product.feature`
- `tests/Features/inventory-item/decrease-stock.feature`

### Cross-domain

```text
tests/Features/cross-domain/<flow-name>.feature
```

例：

- `tests/Features/cross-domain/place-order-and-reserve-stock.feature`

### End-to-end

```text
tests/Features/e2e/<journey-name>.feature
```

例：

- `tests/Features/e2e/customer-places-order.feature`

## 4. 命名規則

- 檔名使用 kebab-case
- 優先使用 use case / flow 名稱，不要使用模糊技術名稱
- 一個 `.feature` 檔應聚焦一個主要 use case、跨域流程、或完整旅程

建議：

- `place-order.feature`
- `cancel-order.feature`
- `product-outbox-publication.feature`

避免：

- `OrderTests.feature`
- `Misc.feature`
- `Scenario1.feature`

## 5. 與 `.dev/specs/tests/` 的分工

### `.feature` 應承載

- Feature / Rule / Scenario 的可讀 Gherkin 流程
- Happy path、failure path、edge case
- 對外可觀察的 Given / When / Then

### `.dev/specs/tests/*.test-spec.md` 應承載

- Related production spec
- assertion notes
- setup / fixture notes
- test level
- event / message / persistence verification 補充
- coverage gaps
- deferred cases
- `.feature` 檔對應路徑

簡單判斷：

- 若目標是讓人或工具直接閱讀 / 執行 BDD scenario -> 放 `tests/Features/`
- 若目標是保留測試設計脈絡與補充規格 -> 放 `.dev/specs/tests/`

## 6. Step Definitions 與測試程式

step definitions 應放在測試專案內，並與 `.feature` 維持清楚對應。

建議：

```text
tests/<TargetProject>.Tests/Steps/
tests/<TargetProject>.Tests/Fixtures/
tests/<TargetProject>.Tests/Support/
```

若專案採用集中式 BDD 測試專案，也可使用：

```text
tests/Features/Steps/
tests/Features/Support/
```

原則：

- `.feature` 靠近測試資產
- step definitions 不放 `.dev/`
- fixture / support code 不和規格文件混放

## 7. 與 Skill / Workflow 的關係

`bdd-gwt-test-designer` 預設先產出 scenario 設計與測試規格資訊。若要進一步落成正式 Gherkin：

1. 以 `.dev/specs/domains/` 作為 production behavior 真相來源
2. 在 `.dev/specs/tests/` 沉澱 scenario 設計與 assertion notes
3. 將可執行 Gherkin 落到 `tests/Features/`
4. 在 test spec 中註記對應 `.feature` 路徑

## 8. 既有範例的定位

`.dev/standards/examples/**/.feature` 僅為示例，不是正式存放位置。

正式新建或維護中的 `.feature` 一律依本文件放在 `tests/Features/`。

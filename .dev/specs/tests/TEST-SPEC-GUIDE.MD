# Test Spec Guide

本指南定義如何在本 repo 內撰寫測試規格，特別適用於 BDD、TDD、Given-When-Then 與 scenario-first 開發。

`.feature` 正式存放規範見 [GHERKIN-FEATURE-STORAGE-GUIDE.MD](./GHERKIN-FEATURE-STORAGE-GUIDE.MD)。

## 1. 什麼情況要建立 test spec

建議在下列情況建立：

- 新 use case 要採 BDD/TDD 開發
- 跨 bounded context 的流程需要明確驗證路徑
- 一個 use case 有多個 business branch，需要先拆 scenario
- 要把 acceptance criteria 轉成測試設計

## 2. 與 production spec 的先後順序

預設順序：

1. `.dev/requirement/`
2. `.dev/specs/domains/`
3. `.dev/specs/tests/`
4. 測試設計 / 測試實作

例外：

- 若你採 TDD，test spec 可以和 `.dev/specs/domains/` 幾乎同步建立
- 但 test spec 不應取代 production spec，因為兩者關心的資訊不同

## 3. 檔名建議

- `[use-case].test-spec.md`
- 例：
  - `place-order.test-spec.md`
  - `decrease-stock.test-spec.md`
  - `ship-order.test-spec.md`

## 3.1 目錄建議

domain-local test spec 應依測試目標分類：

- `.dev/specs/tests/<domain>/aggregate/<aggregate-name>.test-spec.md`
- `.dev/specs/tests/<domain>/use-cases/<use-case>.test-spec.md`
- `.dev/specs/tests/<domain>/integration/<target-name>.test-spec.md`

以下分類為可選，只有真的有內容再建立：

- `.dev/specs/tests/<domain>/app-services/<service-name>.test-spec.md`
- `.dev/specs/tests/<domain>/domain-services/<service-name>.test-spec.md`

跨 bounded context 或完整旅程不要硬掛在某個 domain 之下：

- `.dev/specs/tests/cross-domain/<flow-name>.test-spec.md`
- `.dev/specs/tests/e2e/<journey-name>.test-spec.md`

對應的正式 Gherkin `.feature` 建議放在：

- `tests/Features/<domain>/<use-case>.feature`
- `tests/Features/cross-domain/<flow-name>.feature`
- `tests/Features/e2e/<journey-name>.feature`

## 4. 建議章節

```markdown
# <Use Case> Test Spec

## Scope

## Related Production Spec

## Scenario List

## Given-When-Then

## Assertions

## Test Level

## Notes / Deferred Cases
```

## 5. Scenario 撰寫規則

每個 scenario 至少要說清楚：

- Given: 前置狀態與測試資料
- When: 觸發的 use case / command / event
- Then: 可觀察結果

Then 可包含：

- aggregate state
- domain event
- integration event
- returned dto / result
- error or failure branch

## 6. Test Level 標記

建議在每個 test spec 標記主要驗證層級：

- `unit`
- `application`
- `integration`
- `contract`
- `end-to-end`

常見對應：

- `aggregate/` -> `unit` 或 `application`
- `use-cases/` -> `application`
- `integration/` -> `integration` 或 `contract`
- `cross-domain/` -> `integration` 或 `contract`
- `e2e/` -> `end-to-end`

一份 test spec 可以有主層級與次層級，但應有明確主層級。

## 7. 對分散式系統的補充

若 use case 涉及跨 bounded context 或 MQ 行為，應另外記錄：

- trigger event / command
- expected integration contract
- idempotency concern
- retry / duplicate delivery concern
- eventual consistency expectation

## 8. 與技能/流程的關係

- `.dev/specs/tests/` 是測試意圖的正式文件區
- `bdd-gwt-test-designer` 可把 requirement/spec 轉成此區的 scenarios
- `bdd-gwt-test-designer` 應同時回傳建議存放類別，例如 `use-cases/`、`integration/`、`cross-domain/`
- 後續 test generation 或實作時，正式 `.feature` 應建立在 `tests/Features/`，而不是 `.dev/specs/tests/`
- `.dev/specs/tests/` 應保留 assertion notes、coverage gaps、追溯資訊與非 Gherkin 補充說明

## 9. 最小完成定義

一份 test spec 至少應滿足：

- 對應到一份既有 production spec
- 至少列出 happy path
- 至少列出一個 failure / edge case
- 明確標出主要驗證層級

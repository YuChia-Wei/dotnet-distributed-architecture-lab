# Spec Guide

本文件定義 `.dev/specs/` 內規格文件的格式與撰寫方式，並整合 `SPEC-ORGANIZATION-GUIDE.md` 的組織規範。

`.dev/specs/` 目前分成兩類：

- `domains/`
  - production-facing behavior specs
- `tests/`
  - BDD/TDD-oriented test specs and scenario design artifacts

## 0) Terminology Boundary

- `use case`
  - production behavior 的主名稱，例如 `CreateProduct`
- `command` / `query`
  - 該 use case 的 request model
- `handler`
  - 程式碼中的 application executor

spec 應優先描述：

- 系統要完成的 use case
- 對應的 aggregate / domain event / repository / output

而不是先描述：

- `CreateProductCommandHandler`
- `CreateProductUseCaseService`

換句話說：

- `use case` 是 spec 的主語
- `command` / `query` 與 `handler` 是實作映射，不必成為 spec 主檔名

完整詞彙規則見 [`../standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD`](../standards/USECASE-COMMAND-HANDLER-RELATIONSHIP.MD)

## 1) Directory & Naming Rules
請先遵守：
- `SPEC-ORGANIZATION-GUIDE.MD`
- Aggregate 為最小邊界

production spec 應放在：

- `.dev/specs/domains/<domain>/<entity|usecase|adapter>/...`

test spec 應放在：

- `.dev/specs/tests/<domain>/aggregate/<aggregate-name>.test-spec.md`
- `.dev/specs/tests/<domain>/use-cases/<use-case>.test-spec.md`
- `.dev/specs/tests/<domain>/integration/<target-name>.test-spec.md`
- 視需要再加：`.dev/specs/tests/<domain>/app-services/`、`.dev/specs/tests/<domain>/domain-services/`
- 跨 domain 流程：`.dev/specs/tests/cross-domain/<flow-name>.test-spec.md`
- 端對端旅程：`.dev/specs/tests/e2e/<journey-name>.test-spec.md`

### Use Case Spec
- 檔名格式：`[action]-[aggregate].json`
- 例：`create-product.json`, `estimate-pbi.json`

### Entity / Value Object Spec
- 檔名格式：`[aggregate]-spec.md` 或 `*-spec.json`

### Adapter / Controller Spec
- 檔名格式：`[action]-[aggregate]-controller.json`

## 2) Use Case Spec (JSON)
### Required Keys
- `useCase`
- `behavior`
- `input`
- `aggregate`
- `aggregateId`
- `method`
- `domainEvent`
- `repository`
- `output`

### Interpretation Rules

- `useCase`
  - business operation 名稱，不是 class 名稱
- `input`
  - 對應 command / query request model 的資料形狀
- `method`
  - aggregate constructor、aggregate method、或其他主要 domain entry point
- `repository`
  - command side aggregate persistence 或 query-side 主要資料存取協作者
- `output`
  - handler / use case 完成後回傳的 result DTO 或 output model

### Optional / Recommended Keys
- `domainModelNotes`
- `constructorPreconditions`
- `constructorPostconditions`
- `aggregates`
- `domainEvents`
- `entities`
- `valueObjects`
- `enums`

### Example (minimal)
```json
{
  "useCase": "CreateProduct",
  "behavior": "Create a new product",
  "input": [{ "name": "productId", "type": "String" }],
  "aggregate": "Product",
  "aggregateId": "ProductId",
  "method": "Product constructor",
  "domainEvent": "ProductEvents.ProductCreated",
  "repository": "ProductRepository",
  "output": "CqrsOutput with productId"
}
```

## 3) Adapter / Controller Spec (JSON)
### Required Keys
- `useCase`
- `behavior`
- `spec.basePath`
- `spec.endpoints`

### Recommended
- `spec.errorMapping`
- `contracts.dtos`
- `policies.validation`
- `policies.idempotency`
- `policies.observability`

### Example (minimal)
```json
{
  "useCase": "CreateProductController",
  "behavior": "Create a new product",
  "spec": {
    "basePath": "/v1/api/products",
    "endpoints": [
      { "method": "POST", "path": "", "summary": "Create Product" }
    ]
  }
}
```

## 4) Entity / Value Object Spec (JSON)
### Required Keys
- `entity`
- `type`
- `package`
- `description`
- `attributes`

### Example (from Hours)
```json
{
  "entity": "Hours",
  "type": "ValueObject",
  "package": "tw.teddysoft.aiscrum.common.entity",
  "description": "代表時數的值物件，支援小數點計算",
  "attributes": [
    { "name": "value", "type": "BigDecimal", "constraint": "nullable, >= 0, <= 99999" }
  ]
}
```

## 5) Cross References
每份 spec 必須能回指到：
- 對應 Aggregate
- 相關 Domain Event
- 相關 Use Case / Controller

## 6) Review Checklist
- 檔案是否在正確的 Aggregate 目錄
- Use Case / Adapter / Entity 結構是否符合 JSON 格式
- 是否包含必要欄位
- 是否能對應到實際程式碼命名

## 7) Boundary with Test Specs

- `.dev/specs/domains/` 回答「系統應該做什麼」
- `.dev/specs/tests/` 回答「我要如何驗證它真的做到」
- test spec 不應取代 production spec
- test spec 應優先按測試目標分類，而不是把所有 scenario 平鋪在 `<domain>/`

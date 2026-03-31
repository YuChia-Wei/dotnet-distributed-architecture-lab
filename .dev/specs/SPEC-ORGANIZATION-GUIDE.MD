# Spec 檔案組織指南

> 此指南說明如何正確組織 spec 檔案，以反映領域模型的 Aggregate 邊界。

## 📁 目錄結構原則

目前 `.dev/specs/` 建議分成：

- `domains/`
  - 依 bounded context / aggregate 放 production-facing specs
- `tests/`
  - 依 bounded context / 測試目標類型 放 test specs

### ✅ 正確結構
```text
.dev/specs/
├── domains/
│   ├── product/
│   │   ├── entity/
│   │   │   └── product-spec.md
│   │   └── usecase/
│   │       ├── create-product.json
│   │       └── update-product.json
│   ├── order/
│   │   ├── entity/
│   │   │   └── order-spec.md
│   │   └── usecase/
│   │       ├── place-order.json
│   │       ├── ship-order.json
│   │       ├── deliver-order.json
│   │       └── cancel-order.json
│   └── inventory-item/
│       ├── entity/
│       │   └── inventory-item-spec.md
│       └── usecase/
│           ├── decrease-stock.json
│           ├── increase-stock.json
│           └── restock.json
└── tests/
    ├── order/
    │   ├── aggregate/
    │   ├── integration/
    │   └── use-cases/
    │       └── place-order.test-spec.md
    ├── inventory-item/
    │   └── use-cases/
    │       └── decrease-stock.test-spec.md
    ├── cross-domain/
    └── e2e/
```

### ❌ 錯誤結構
```text
.dev/specs/
└── domains/
    └── product/
        └── usecase/
        ├── create-product.json
        ├── create-pbi.json        ❌ PBI 不應在 product 下
        └── create-sprint.json     ❌ Sprint 不應在 product 下
```

## 🎯 判斷 Spec 應該放在哪裡

### 步驟 1：識別主要 Aggregate
問自己：「這個 Use Case 主要操作哪個 Aggregate？」

### 步驟 2：檢查 Aggregate 名稱
- `CreateProduct` → Product Aggregate → `domains/product/usecase/`
- `CreateProductBacklogItem` → PBI Aggregate → `domains/pbi/usecase/`
- `CreateSprint` → Sprint Aggregate → `domains/sprint/usecase/`

### 步驟 3：驗證決定
使用 [AGGREGATE-IDENTIFICATION-CHECKLIST.md](../../.ai/AGGREGATE-IDENTIFICATION-CHECKLIST.md)

## 📝 命名規範

### Use Case Spec 檔案
- 格式：`[action]-[aggregate].json`
- 範例：
  - `create-product.json`
  - `create-pbi.json`（不是 create-product-backlog-item.json）
  - `estimate-pbi.json`

### Entity Spec 檔案
- 格式：`[aggregate]-spec.md`
- 範例：
  - `product-spec.md`
  - `pbi-spec.md`
  - `sprint-spec.md`

### Test Spec 檔案
- 格式：`[target].test-spec.md`
- 範例：
  - `place-order.test-spec.md`
  - `decrease-stock.test-spec.md`
  - `order-fulfillment-flow.test-spec.md`

### Test Spec 目錄規則
- aggregate 驗證：`tests/<domain>/aggregate/<aggregate-name>.test-spec.md`
- use case 驗證：`tests/<domain>/use-cases/<use-case>.test-spec.md`
- integration 驗證：`tests/<domain>/integration/<target-name>.test-spec.md`
- 視需要再加：
  - `tests/<domain>/app-services/<service-name>.test-spec.md`
  - `tests/<domain>/domain-services/<service-name>.test-spec.md`
- 跨 domain 流程：
  - `tests/cross-domain/<flow-name>.test-spec.md`
- E2E 旅程：
  - `tests/e2e/<journey-name>.test-spec.md`

## ⚠️ 常見錯誤

### 錯誤 1：根據關聯關係組織
```text
❌ domains/product/usecase/create-pbi.json
   理由：雖然 PBI 有 ProductId，但 PBI 是獨立 Aggregate

✅ domains/pbi/usecase/create-pbi.json
```

### 錯誤 2：根據名稱前綴組織
```text
❌ domains/product/usecase/create-product-backlog-item.json
   理由：名稱誤導，PBI 不是 Product 的一部分

✅ domains/pbi/usecase/create-pbi.json
```

### 錯誤 3：集中式組織
```text
❌ specs/usecases/create-product.json
❌ specs/usecases/create-pbi.json
   理由：失去 Aggregate 邊界的可見性

✅ specs/domains/product/usecase/create-product.json
✅ specs/domains/pbi/usecase/create-pbi.json
```

## 🔄 遷移指南

如果發現 spec 檔案位置錯誤：

1. **創建正確的目錄結構**
   ```bash
   mkdir -p .dev/specs/domains/[aggregate]/usecase
   ```

2. **移動檔案**
   ```bash
   mv .dev/specs/domains/product/usecase/create-sprint.json \
      .dev/specs/domains/pbi/usecase/
   ```

3. **更新相關引用**
   - task-*.json 中的 spec.useCase 路徑
   - 測試檔案中的引用
   - 文檔中的連結

4. **驗證**
   ```bash
   # 確認沒有遺漏的引用
   grep -r "domains/product/usecase/create-pbi" .
   ```

## 📊 Aggregate 對照表

| Aggregate | Spec 目錄 | 主要 Use Cases |
|-----------|----------|----------------|
| Product | `domains/product/` | CreateProduct, UpdateProduct |
| Order | `domains/order/` | PlaceOrder, ShipOrder, DeliverOrder, CancelOrder |
| InventoryItem | `domains/inventory-item/` | DecreaseStock, IncreaseStock, Restock |

## 🚀 最佳實踐

1. **新增 Spec 前先確認 Aggregate**
   - 查看 [DOMAIN-MODEL.md](../../.ai/DOMAIN-MODEL.md)
   - 使用 [AGGREGATE-IDENTIFICATION-CHECKLIST.md](../../.ai/AGGREGATE-IDENTIFICATION-CHECKLIST.md)

2. **保持一致性**
   - Spec 結構應與程式碼套件結構一致
   - 命名應與領域術語一致

3. **定期審查**
   - Code Review 時檢查 spec 位置
   - 發現錯誤立即修正

## 🧪 Test Spec 補充規則

- test spec 與 production spec 應使用同一組 domain / aggregate 視角
- test spec 優先對應既有 production spec，而不是自成孤島
- 若採 BDD / TDD，請把 scenario 設計放在 `.dev/specs/tests/`
- test spec 應優先按測試目標分類，例如 `use-cases/`、`integration/`
- `cross-domain/` 與 `e2e/` 不應隨意掛在單一 domain 底下

## 📅 更新記錄

- **2025-08-12**: 初始版本，建立 spec 組織原則
- **2025-08-12**: 將 create-pbi.json 從 product/ 移至 pbi/
- **2026-03-31**: 新增 typed test spec taxonomy 與 cross-domain / e2e 規則

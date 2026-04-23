# Problem Frame Semantics Mapping

本檔案提供 `aggregate.yaml` 中常見 semantic tags 的最小約定，供 code review 與後續 problem-frame authoring 參考。

## 目的

- 讓 `aggregate.yaml` 的欄位語意可被穩定重用
- 讓 `.dev/standards/CODE-REVIEW-CHECKLIST.md` 提到的 semantics 有可對照來源
- 避免每個專案用不同字詞描述同一種不變條件

## Core Semantics

### `identity`

- 定義：Aggregate 或 Entity 的穩定識別值
- 規則：
  - 建立後不可變更
  - 不應存在修改 identity 的 command / event

### `value_immutable`

- 定義：建立後不允許被更新的值
- 規則：
  - 無 setter
  - 不應有對應的 update event

### `collection_reference_immutable`

- 定義：集合參考建立一次，不可被替換，但可安全改變內容
- 規則：
  - 集合應初始化一次
  - 只能透過 Aggregate method 修改內容

### `soft_delete_flag`

- 定義：表示業務上已失效但仍需保留紀錄
- 規則：
  - 刪除後行為受限
  - 應有對應 event 或明確狀態轉換

### `optimistic_concurrency_version`

- 定義：用於併發控制的版本值
- 規則：
  - 由基礎設施或框架管理
  - 不由業務命令直接指定

### `external_authority`

- 定義：本系統不能自行決定，必須以外部系統結果為準的欄位或狀態
- 例子：
  - Payment authorization result
  - External customer status
  - Carrier shipment acceptance

### `idempotency_key`

- 定義：用來識別重複請求或重送回調的穩定鍵
- 規則：
  - 同一 key 的重試不應造成重複副作用
  - 應能追溯到 command 或 external callback

## 使用建議

- 若某欄位語意已被這裡涵蓋，優先重用這些 tag。
- 若專案需要新語意，應先在此檔補充，再在 `aggregate.yaml` 引用。

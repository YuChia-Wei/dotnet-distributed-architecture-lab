# REST API Resource Path Rationale

## Decision Pattern

預設採用：

- 建立端點使用巢狀路徑
- 資源操作使用扁平路徑

例如：

- `POST /products/{productId}/pbis`
- `GET /pbis/{pbiId}`
- `PATCH /pbis/{pbiId}`

## Why

### 1. 建立時需要表達歸屬上下文

建立操作通常需要明確表示「在哪個父集合之下新增」。  
巢狀路徑能直接把這個上下文放進 URL，而不是只藏在 body。

### 2. 資源建立後應被視為獨立 identity

一旦資源已存在，它應該由自己的 identity 被尋址，而不是永遠附著在父資源路徑下。  
這更符合 DDD 中 aggregate root 的獨立生命週期。

### 3. 路徑語意更穩定

若資源未來可能搬移、重組、或不再綁定同一父資源，扁平資源路徑較不易受影響。

## Why Not

### 全部都巢狀

缺點：

- 把資源看成父資源的附屬品
- 容易弱化 aggregate root 的獨立 identity
- 路徑會越長越深

### 全部都扁平

缺點：

- 建立時失去「在哪個集合中新增」的語意
- 父資源不存在時的錯誤處理較不直觀

## Practical Rule

- create: 優先巢狀
- read/update/delete by id: 優先扁平
- collection query: 視需要可同時提供全域與父資源 scoped 版本

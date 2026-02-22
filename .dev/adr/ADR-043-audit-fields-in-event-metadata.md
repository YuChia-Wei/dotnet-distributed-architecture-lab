# ADR-043: 審計欄位存放在 Event Metadata 而非 Entity (.NET)

## Status
Accepted

## Date
2025-09-07

## Context
審計資訊（creatorId、updaterId、createdAt、updatedAt）應該放在哪裡？選項：
1. Aggregate Entity
2. Data/資料庫欄位
3. Domain Event metadata

## Decision
採用選項 3：**審計資訊只存在 Domain Event metadata**。

具體規範：
- Aggregate 不含審計欄位
- Data/表格不含審計欄位（移除 NOT NULL）
- 審計資訊從 Event Store 查詢

## Rationale
1. **保持領域模型純粹**
2. **避免基礎設施污染**
3. **Event Store 本身就是審計軌跡**

## Implementation Examples

### ✅ 正確：Event Metadata
```csharp
public Product(ProductId id, ProductName name, string userId)
{
    var metadata = new Dictionary<string, string>
    {
        ["creatorId"] = userId,
        ["createdAt"] = DateTimeOffset.UtcNow.ToString("O")
    };

    Apply(new ProductCreated(id, name, metadata, Guid.NewGuid(), DateProvider.Now()));
}
```

### ❌ 錯誤：Entity/Data 加入審計欄位
```csharp
public class Product
{
    public string CreatorId { get; private set; } // ❌
}

public class ProductData
{
    public string CreatorId { get; set; } // ❌
}
```

## How to Query Audit Information
```csharp
public string GetProductCreator(ProductId productId)
{
    var events = messageStore.GetEvents(productId.Value);
    var created = events.First(e => e.Type == "ProductCreated");
    return created.Metadata["creatorId"];
}
```

## Consequences
- ✅ Domain 純粹
- ✅ Event Store 提供不可變審計
- ❌ 需要額外查詢

## Notes
此決策適用所有 Aggregate。

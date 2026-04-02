# Mapper 編碼規範 (.NET)

本文件定義 Mapper 類別的編碼標準，負責在不同層級之間轉換資料物件。

---

## 📌 概述

Mapper 負責 Domain 與 DTO / Data 物件的轉換。

- **Domain → Data**: 將領域物件轉換為持久化物件
- **Data → Domain**: 將持久化物件轉換回領域物件
- **Domain → DTO**: 將領域物件轉換為資料傳輸物件

---

## 🏷️ Pattern 標記（自動化檢查用）

以下標記供自動化 Code Review 腳本使用：

```yaml
# Mapper 規則
Pattern (required, any): static class|sealed class
Pattern (required): ArgumentNullException\.ThrowIfNull

# 禁止規則
Pattern (forbidden, ignore-comment): I[A-Za-z0-9]*Repository|UseCase|Handler
```

---

## 🔴 必須遵守的規則 (MUST FOLLOW)

### 1. 使用 Static Methods

Mapper 應該使用靜態方法，避免建立實例：

```csharp
// ✅ 正確：使用 static class 和 static methods
public static class ProductMapper
{
    public static ProductData ToData(Product aggregate)
    {
        ArgumentNullException.ThrowIfNull(aggregate);
        
        return new ProductData
        {
            Id = aggregate.Id.Value,
            Name = aggregate.Name,
            State = aggregate.State.ToString(),
            IsDeleted = aggregate.IsDeleted,
            CreatedAt = aggregate.CreatedAt,
            UpdatedAt = aggregate.UpdatedAt
        };
    }
    
    public static Product ToDomain(ProductData data)
    {
        ArgumentNullException.ThrowIfNull(data);
        
        // 從 Event Sourcing 重建
        if (data.DomainEvents?.Any() == true)
        {
            var events = data.DomainEvents
                .Select(DomainEventMapper.ToDomain)
                .ToList();
            
            var product = new Product(events);
            product.ClearDomainEvents();
            return product;
        }
        
        // 從當前狀態重建
        return new Product(
            ProductId.From(data.Id),
            data.Name,
            data.CreatorId
        );
    }
}

// ❌ 錯誤：建立 Mapper 實例
public class ProductMapper
{
    public ProductData ToData(Product aggregate)  // 非 static
    {
        // ...
    }
}
```

---

### 2. 完整的雙向轉換

`ToData()` 和 `ToDomain()` 必須是對稱的：

```csharp
// ✅ 正確：ToData 序列化，ToDomain 反序列化
public static class ProductMapper
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        WriteIndented = false
    };

    public static ProductData ToData(Product aggregate)
    {
        var data = new ProductData
        {
            Id = aggregate.Id.Value,
            Name = aggregate.Name,
            State = aggregate.State.ToString()
        };
        
        // 序列化複雜物件
        if (aggregate.DefinitionOfDone is not null)
        {
            data.DefinitionOfDoneJson = JsonSerializer.Serialize(
                aggregate.DefinitionOfDone, JsonOptions);
        }
        
        return data;
    }

    public static Product ToDomain(ProductData data)
    {
        var product = new Product(
            ProductId.From(data.Id),
            data.Name,
            data.CreatorId
        );
        
        // 反序列化複雜物件
        if (!string.IsNullOrEmpty(data.DefinitionOfDoneJson))
        {
            var dod = JsonSerializer.Deserialize<DefinitionOfDone>(
                data.DefinitionOfDoneJson, JsonOptions);
            product.DefineDefinitionOfDone(dod);
        }
        
        return product;
    }
}
```

補充要求：

- 優先沿用單一 `JsonSerializerOptions`
- 複雜物件序列化失敗時應優雅降級，不應讓 mapper 中斷整個流程
- 若 data 內含 domain events，`ToDomain()` 應優先走 event-based rebuild

---

### 3. IsDeleted 欄位必須映射

Aggregate Root 的 Mapper 必須處理 `IsDeleted` 欄位：

```csharp
// ✅ 正確：映射 IsDeleted 欄位
public static ProductData ToData(Product aggregate)
{
    return new ProductData
    {
        Id = aggregate.Id.Value,
        Name = aggregate.Name,
        IsDeleted = aggregate.IsDeleted,  // MANDATORY!
        // ...其他欄位
    };
}

public static Product ToDomain(ProductData data)
{
    var product = new Product(
        ProductId.From(data.Id),
        data.Name,
        data.CreatorId
    );
    
    // MANDATORY: 恢復 IsDeleted 狀態
    if (data.IsDeleted)
    {
        product.MarkAsDeleted();
    }
    
    return product;
}

// ❌ 錯誤：遺漏 IsDeleted 映射
public static ProductData ToData(Product aggregate)
{
    return new ProductData
    {
        Id = aggregate.Id.Value,
        Name = aggregate.Name
        // 缺少 IsDeleted！
    };
}
```

---

### 4. Domain Events 與 Metadata 必須映射

若 mapper 參與 write model / outbox round-trip，必須處理：

- domain events
- event metadata
- stream identity（若該 aggregate 採 event/outbox 模式）

```csharp
public static ProductData ToData(Product aggregate)
{
    return new ProductData
    {
        Id = aggregate.Id.Value,
        DomainEventDatas = aggregate.DomainEvents
            .Select(DomainEventMapper.ToData)
            .ToList(),
        StreamName = aggregate.StreamName
    };
}
```

```csharp
public static Product ToDomain(ProductData data)
{
    if (data.DomainEventDatas is { Count: > 0 })
    {
        var events = data.DomainEventDatas
            .Select(DomainEventMapper.ToDomain)
            .Cast<IDomainEvent>()
            .ToList();

        return new Product(events);
    }

    // fallback rebuild by current state
}
```

---

## 🎯 處理 Value Objects

### Record Value Objects

```csharp
// Value Object 定義
public sealed record ProductId(string Value)
{
    public static ProductId From(string value) => new(value);
}

// Mapper 中使用
public static ProductData ToData(Product aggregate)
{
    return new ProductData
    {
        Id = aggregate.Id.Value,  // 取出內部值
        // ...
    };
}

public static Product ToDomain(ProductData data)
{
    var product = new Product(
        ProductId.From(data.Id),  // 重建 Value Object
        // ...
    );
    return product;
}
```

---

## 🎯 錯誤處理策略

### 優雅降級原則

```csharp
// ✅ 正確：捕獲異常，記錄但不中斷
public static Product ToDomain(ProductData data)
{
    var product = new Product(...);
    
    if (!string.IsNullOrEmpty(data.DefinitionOfDoneJson))
    {
        try
        {
            var dod = JsonSerializer.Deserialize<DefinitionOfDone>(
                data.DefinitionOfDoneJson, JsonOptions);
            product.DefineDefinitionOfDone(dod);
        }
        catch (JsonException ex)
        {
            // 可選：記錄錯誤用於除錯
            // _logger.LogWarning(ex, "Failed to deserialize DefinitionOfDone");
            
            // 優雅降級：繼續處理，不中斷流程
        }
    }
    
    return product;
}

// ❌ 錯誤：讓異常傳播
public static Product ToDomain(ProductData data)
{
    var dod = JsonSerializer.Deserialize<DefinitionOfDone>(
        data.DefinitionOfDoneJson, JsonOptions);  // 可能拋出異常
    // ...
}
```

---

### JSON 失敗處理原則

- 可以記錄 warning
- 不應因單一複雜欄位序列化/反序列化失敗就讓整個 mapping 流程失敗
- 但不得默默遺漏關鍵 business identity

---

## ⚠️ 常見錯誤

### Aggregate 新增狀態但 Data/Mapper 未同步更新

**這是最容易遺漏的錯誤！**

```csharp
// ❌ 錯誤：Aggregate 新增了欄位，但 Mapper 沒有處理
// Product.cs
public class Product : AggregateRoot<ProductId>
{
    private readonly List<CommittedSprint> _committedSprints = new();  // 新增欄位
    
    public void CommitSprint(SprintId sprintId)
    {
        // ... 業務邏輯
    }
}

// ProductMapper.cs - ToData() 沒更新 ❌
// ProductMapper.cs - ToDomain() 沒更新 ❌
// ProductData.cs - 沒有對應欄位 ❌

// 結果：Save() 後再 FindById()，CommittedSprints 會是空的！
```

```csharp
// ✅ 正確：三個檔案必須同步更新

// 1. ProductData.cs - 新增欄位
public class ProductData
{
    public string? CommittedSprintsJson { get; set; }
}

// 2. ProductMapper.ToData() - 序列化
data.CommittedSprintsJson = JsonSerializer.Serialize(
    aggregate.CommittedSprints.Select(s => s.SprintId.Value).ToList(),
    JsonOptions);

// 3. ProductMapper.ToDomain() - 反序列化
if (!string.IsNullOrEmpty(data.CommittedSprintsJson))
{
    var sprintIds = JsonSerializer.Deserialize<List<string>>(
        data.CommittedSprintsJson, JsonOptions);
    foreach (var id in sprintIds ?? [])
    {
        product.CommitSprint(SprintId.From(id));
    }
}
```

---

## 🔍 檢查清單

### Mapper 結構
- [ ] 使用 `static class` 和 `static methods`
- [ ] 處理 null 輸入 (`ArgumentNullException.ThrowIfNull`)
- [ ] 配置 `JsonSerializerOptions`

### ToData 方法
- [ ] 映射所有基本欄位
- [ ] 序列化複雜物件為 JSON
- [ ] 包含 `IsDeleted` 欄位
- [ ] 處理序列化錯誤
- [ ] 如屬 write-model mapper，包含 domain events / metadata / stream identity

### ToDomain 方法
- [ ] 優先從 events 重建（Event Sourcing）
- [ ] 支援從狀態重建
- [ ] 反序列化所有複雜物件
- [ ] 恢復 `IsDeleted` 狀態
- [ ] 呼叫 `ClearDomainEvents()`
- [ ] 反序列化失敗時採優雅降級，不讓整體流程中斷

### ToDto 方法
- [ ] 有 Domain → DTO 方法
- [ ] 有 Data → DTO 方法（for Projection）

---

## 📂 程式碼範例

更多完整範例請參考：

| 範例 | 路徑 |
|------|------|
| Mapper 範例 | [../examples/mapper/](../examples/mapper/) |
| Outbox Mapper 範例 | [../examples/outbox/](../examples/outbox/) |
| DTO 範例 | [../examples/dto/](../examples/dto/) |

---

## 相關文件

- [aggregate-standards.md](aggregate-standards.md)
- [repository-standards.md](repository-standards.md)
- [projection-standards.md](projection-standards.md)
- [../../adr/ADR-041-mapper-serialization-requirements.md](../../adr/ADR-041-mapper-serialization-requirements.md)

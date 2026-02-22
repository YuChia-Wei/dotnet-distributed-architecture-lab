# ADR-041: Mapper Serialization Requirements (.NET)

## Status
Accepted

## Context
Mapper 需要正確序列化/反序列化複雜物件（例如 `DefinitionOfDone`），並能處理事件重建。若序列化失敗，不應中斷流程。

## Decision

### 1. JSON 序列化配置規範
使用 `System.Text.Json` 並統一配置（包含 `DateTimeOffset`/`Instant` 等時間欄位）：

```csharp
private static readonly JsonSerializerOptions JsonOptions = new()
{
    PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
    WriteIndented = false,
    Converters = { new JsonStringEnumConverter() }
};
```

### 2. toData() 實作規範
- 必須處理所有複雜物件序列化
- 序列化失敗要 **優雅降級**（不可中斷流程）
- 必須包含 domain events 與 metadata

```csharp
public static ProductData ToData(Product product)
{
    var data = new ProductData
    {
        ProductId = product.Id.Value
    };

    if (product.DefinitionOfDone is not null)
    {
        try
        {
            data.DefinitionOfDone = JsonSerializer.Serialize(product.DefinitionOfDone, JsonOptions);
        }
        catch
        {
            data.DefinitionOfDone = null;
        }
    }

    data.DomainEventDatas = product.DomainEvents.Select(DomainEventMapper.ToData).ToList();
    data.StreamName = product.StreamName;
    return data;
}
```

### 3. toDomain() 實作規範
- 優先從 events 重建（Event Sourcing）
- 若無 events，從當前狀態重建
- 必須完整還原複雜物件

```csharp
public static Product ToDomain(ProductData data)
{
    if (data.DomainEventDatas is { Count: > 0 })
    {
        var events = data.DomainEventDatas
            .Select(DomainEventMapper.ToDomain)
            .Cast<ProductEvents>()
            .ToList();
        return new Product(events);
    }

    var product = new Product(/*...*/);

    if (!string.IsNullOrWhiteSpace(data.DefinitionOfDone))
    {
        try
        {
            var dod = JsonSerializer.Deserialize<DefinitionOfDone>(data.DefinitionOfDone, JsonOptions);
            if (dod is not null)
            {
                product.DefineDefinitionOfDone(dod.Name, dod.Criteria, dod.Note, dod.DefinedAt);
            }
        }
        catch
        {
            // 優雅降級
        }
    }

    return product;
}
```

### 4. Mapper 類別結構規範
```csharp
public static class [Aggregate]Mapper
{
    private static readonly JsonSerializerOptions JsonOptions = CreateOptions();
    private static readonly IOutboxMapper<[Aggregate], [Aggregate]Data> OutboxMapper = new Mapper();

    // DTO mapping
    public static [Aggregate]Dto ToDto([Aggregate] aggregate) { }

    // Domain/Data mapping
    public static [Aggregate]Data ToData([Aggregate] aggregate) { }
    public static [Aggregate] ToDomain([Aggregate]Data data) { }

    public static IOutboxMapper<[Aggregate], [Aggregate]Data> NewMapper() => OutboxMapper;

    private sealed class Mapper : IOutboxMapper<[Aggregate], [Aggregate]Data> { }
}
```

## Consequences
- ✅ 序列化一致
- ✅ Domain 還原完整
- ✅ 失敗可容忍
- ⚠️ 需要維護 JsonOptions 一致性

## Implementation Checklist
- [ ] 統一 JsonSerializerOptions
- [ ] toData() 完整序列化
- [ ] toDomain() 完整還原
- [ ] OutboxMapper 內部類別
- [ ] 例外處理（不可拋出）

## Related
- ADR-019: Outbox Pattern Implementation
- ADR-020: Archive Pattern Implementation
- `.dev/standards/coding-standards/mapper-standards.md`

## Date
2025-08-24

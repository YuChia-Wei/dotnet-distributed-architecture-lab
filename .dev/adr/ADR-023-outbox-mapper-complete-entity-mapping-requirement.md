# ADR-023: Outbox Mapper 必須完整映射聚合內所有實體 (.NET)

## 狀態
已採納 (2025-08-24)

## 背景與問題
Outbox pattern 的 mapper 若未完整處理子實體，會造成資料在「保存 → 載入」往返時遺失。

## 決策

### 1. Mapper 實作要求
所有 Outbox Mapper **必須**完整映射所有子實體：

```csharp
// toData(): Domain -> Data
public static ProductBacklogItemData ToData(ProductBacklogItem pbi)
{
    var data = new ProductBacklogItemData();
    // ... 基本屬性

    if (pbi.Tasks is { Count: > 0 })
    {
        data.TaskDatas = pbi.Tasks
            .Select(t => MapTaskToData(t, data))
            .ToList();
    }

    return data;
}

// toDomain(): Data -> Domain
public static ProductBacklogItem ToDomain(ProductBacklogItemData data)
{
    var tasks = data.TaskDatas?.Select(MapTaskToDomain).ToList() ?? new List<Task>();

    return new ProductBacklogItem(
        /* base args */,
        tasks
    );
}
```

### 2. 聚合建構子設計
Aggregate 必須提供「重建用」建構子：

```csharp
public class ProductBacklogItem
{
    public ProductBacklogItem(ProductId id, string name /* ... */)
    {
        // 產生領域事件
    }

    // 重建用建構子（不產生事件）
    public ProductBacklogItem(ProductId id, string name, IEnumerable<Task> tasks /* ... */)
        : this(id, name /* ... */)
    {
        if (tasks is not null)
            _tasks.AddRange(tasks);

        ClearDomainEvents();
    }
}
```

### 3. 驗證機制
- 單元測試必須驗證 `ToData()` → `ToDomain()` 往返不遺失子實體
- Code Review 清單必須檢查 Mapper 完整性

## 後果
- ✅ 資料完整性
- ✅ 避免業務邏輯失敗
- ⚠️ Mapper 複雜度提升

## 實作指引

### 檢查清單
- [ ] `ToData()` 映射所有子實體
- [ ] `ToData()` 正確處理父子關聯
- [ ] `ToDomain()` 重建所有子實體
- [ ] 重建建構子不產生多餘事件
- [ ] 往返測試覆蓋多子實體情境

### 測試範例
```csharp
[Fact]
public void mapper_should_preserve_all_entities_in_round_trip()
{
    var original = CreatePbiWithMultipleTasks();
    var data = ProductBacklogItemMapper.ToData(original);
    var reconstructed = ProductBacklogItemMapper.ToDomain(data);

    Assert.Equal(original.Tasks.Count, reconstructed.Tasks.Count);
}
```

## 相關文件
- `.ai/scripts/check-mapper-compliance.sh`
- `.dev/standards/coding-standards/mapper-standards.md`


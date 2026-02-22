# ADR-021: Aggregate 欄位初始化模式 (.NET)

## 狀態
已接受

## 背景
在實作 ScrumTeam aggregate 時發現嚴重 bug：團隊成員無法累積，每次新增都覆蓋舊資料。原因是集合欄位初始化時機錯誤。

## 問題描述

### 錯誤的實作方式
```csharp
public class ScrumTeam : AggregateRoot<ScrumTeamEvents>
{
    private readonly List<TeamMember> _members;

    public ScrumTeam(IEnumerable<ScrumTeamEvents> domainEvents)
        : base(domainEvents) // 事件重播
    {
        _members = new List<TeamMember>(); // ❌ 這會清空重播結果
    }
}
```

### 問題分析
1. `base(domainEvents)` 會觸發事件重播
2. 重播會呼叫 `When(...)` 處理 `TeamMemberAdded`
3. 若集合在 base() 後初始化，重播結果被清空

## 決策

### 正確的實作方式
```csharp
public class ScrumTeam : AggregateRoot<ScrumTeamEvents>
{
    // ✅ 欄位宣告時初始化（在 base() 之前）
    private readonly List<TeamMember> _members = new();

    public ScrumTeam(IEnumerable<ScrumTeamEvents> domainEvents)
        : base(domainEvents)
    {
    }
}
```

## 規則

### 1. 集合欄位必須在宣告時初始化
- ✅ `private readonly List<Member> _members = new();`
- ❌ `private readonly List<Member> _members;` 然後在建構子中初始化

### 2. 建構子初始化順序（C#）
1. 欄位宣告初始化
2. `base(...)` 呼叫
3. 建構子內其他邏輯

### 3. Mapper 的 ToDomain 實作
```csharp
public static ScrumTeam ToDomain(ScrumTeamData data)
{
    if (data.DomainEventDatas is { Count: > 0 })
    {
        var events = /* convert */;
        return new ScrumTeam(events);
    }

    var scrumTeam = new ScrumTeam(/* basic args */);

    if (data.Members is not null)
    {
        foreach (var member in data.Members)
        {
            scrumTeam.AddMember(/* ... */);
        }
    }

    return scrumTeam;
}
```

## 影響範圍
- 所有包含集合欄位的 Aggregate
- 所有 Mapper 的 `ToDomain`
- Event Sourcing / Outbox 實作

## 檢查清單
- [ ] 所有集合欄位在宣告時初始化
- [ ] 建構子中沒有在 base() 後重新初始化集合
- [ ] `ToDomain` 恢復所有集合狀態
- [ ] 測試驗證集合可累積元素

## 相關文件
- `.dev/standards/coding-standards/aggregate-standards.md`
- `.dev/standards/coding-standards/mapper-standards.md`
- `.ai/AGGREGATE-IMPLEMENTATION-CHECKLIST.md`


# ADR-010: Use Case Service 不使用框架註解 (.NET)

## Status
Accepted

## Context
需要確保 Use Case Service 保持純粹，不因 DI 框架而污染結構。同時避免「自動掃描」導致的隱性註冊與追蹤困難。

## Decision
**Use Case Service 不使用任何 DI 相關 attribute**，一律在 Composition Root 以 `IServiceCollection` 明確註冊。

### 實作方式
```csharp
// ❌ 錯誤：在 Service 類別上做 attribute 註冊
[SomeDiAttribute]
public class ConfigScrumBoardTaskStateService : IConfigScrumBoardTaskStateUseCase
{
    public ConfigScrumBoardTaskStateService(ISprintRepository sprintRepository) { ... }
}

// ✅ 正確：Service 類別保持純 POCO
public class ConfigScrumBoardTaskStateService : IConfigScrumBoardTaskStateUseCase
{
    private readonly ISprintRepository _sprintRepository;

    public ConfigScrumBoardTaskStateService(ISprintRepository sprintRepository)
    {
        _sprintRepository = sprintRepository ?? throw new ArgumentNullException(nameof(sprintRepository));
    }
}

// ✅ 正確：在 Composition Root 顯式註冊
services.AddScoped<IConfigScrumBoardTaskStateUseCase, ConfigScrumBoardTaskStateService>();
```

## Consequences

### 優點
1. **符合 Clean Architecture**：Use Case 不依賴 DI framework
2. **依賴關係清楚**：註冊集中在 Composition Root
3. **可測試性高**：純 POCO 易於單元測試
4. **避免掃描成本**：不依賴 assembly scanning

### 缺點
1. **需要手動註冊**
2. **可能忘記註冊**

### 影響範圍
- Use Case Service
- Projection / Mapper（保持純 POCO）

## Notes
- 這個決策需同步到 code review checklist / prompts
- Code review 必須檢查是否有 DI attribute

## Date
2025-08-17

## Author
AI-SCRUM Team

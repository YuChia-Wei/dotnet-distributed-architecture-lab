# ADR-024: Test Isolation and DomainEventMapper Management (.NET)

## Status
Landed in Standards

## Current Canonical Source

- `.dev/standards/coding-standards/test-standards.md`
- `.dev/guides/design-guides/FRAMEWORK-API-INTEGRATION-GUIDE.md`

## Context
Outbox 整合測試曾出現間歇性失敗：
```
Unsupported event for mapping: SprintCreated
```

原因：
1. 事件型別映射缺少一致的前綴
2. 多個測試覆蓋全域 `DomainEventMapper`，造成測試互相干擾

## Decision

### 1. 統一事件映射前綴
所有事件型別必須帶上固定前綴：
```csharp
public const string MappingPrefix = "Sprint.";
public const string MemberCapacitySet = MappingPrefix + "MemberCapacitySet";
public const string MemberCapacityReforecasted = MappingPrefix + "MemberCapacityReforecasted";
public const string MemberCapacityCleared = MappingPrefix + "MemberCapacityCleared";
```

### 2. 統一使用 Bootstrap 初始化
所有需要事件映射的測試必須統一使用 `BootstrapConfig.Initialize()`：
```csharp
public static class TestBootstrap
{
    [ModuleInitializer]
    public static void Init()
    {
        BootstrapConfig.Initialize();
    }
}
```

### 3. Outbox 測試防禦性初始化
```csharp
public class OutboxIntegrationTests
{
    public OutboxIntegrationTests()
    {
        BootstrapConfig.Initialize();
    }
}
```

## Consequences
- ✅ 測試隔離性提升
- ✅ 映射一致性
- ✅ 消除順序/並行造成的失敗
- ⚠️ 測試有些重複初始化成本

## Lessons Learned
1. 全局狀態會破壞測試隔離
2. 測試應防禦性初始化
3. 事件映射前綴必須一致

## Related ADRs
- ADR-019: Outbox Pattern Implementation
- ADR-031: Reactor Interface Definition

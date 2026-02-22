# Common Pitfalls and Solutions (.NET)

本文件記錄在使用 Sub-agent Workflow 實作時常見的錯誤和解決方案（.NET 版）。

## 🔴 DI / Configuration 問題（高頻）

### 1. 重複的 EF Core 註冊
**錯誤**：`InvalidOperationException: The service collection already contains ... DbContext`

**原因**：多處重複呼叫 `AddDbContext` 或 profile 未隔離。

**解決方案**：
1. 只在 profile-specific configuration 中註冊一次。
2. 使用 `ASPNETCORE_ENVIRONMENT` 控制 InMemory / Outbox。
3. 依 `project-config.yaml` 的 profile 切換。

**預防措施**：
```bash
rg -n "AddDbContext" src
```

### 2. Use Case Input 欄位名稱不一致
**錯誤**：Controller/Handler 讀取欄位名稱不一致導致 null。

**解決方案**：DTO → Input 映射時明確對應欄位。
```csharp
// Wrong
input.ProductId = request.Id;

// Correct
input.Id = request.ProductId;
```

## 🔴 Outbox / Event Sourcing 問題

### 3. Wolverine Outbox 未啟用
**錯誤**：事件未持久化或不出現於 message store。

**解決方案**：
```csharp
services.AddWolverine(opts =>
{
    opts.PersistMessagesWithPostgresql(conn);
    opts.UseDurableOutbox();
});
```

### 4. OutboxMapper 未處理無 events 的重建
**錯誤**：從 DB 讀取時 Aggregate 無狀態。

**解決方案**：
- 有 events → 從 events 重建
- 無 events → 從 stored state 重建並補事件

### 5. 混用 InMemory / Outbox 註冊
**錯誤**：同一個 profile 同時註冊 InMemory 與 Outbox repositories。

**解決方案**：保持 profile 隔離（InMemory / Outbox），只在對應 profile 註冊。

## 🔴 Domain Model / Mapping 問題

### 6. Value Object 缺少 ValueOf/From 方法
**錯誤**：Mapper 或 UseCase 無法一致地建立 VO。

**解決方案**：提供明確的建立方法，例如 `ValueOf(string)` 或 `From(string)`，並保留驗證。

### 7. Projection 直接回傳 EF Entity
**錯誤**：Projection 回傳 EF Core entity 而非 DTO。

**解決方案**：透過 Mapper 投影為 DTO，避免直接暴露資料層。

### 8. Projection 混入 DbContext 邏輯
**錯誤**：Projection 直接繼承 DbContext 或使用 Repository 介面覆寫 EF Core API。

**解決方案**：使用 Adapter / Service 封裝查詢邏輯，Projection 只提供 query 方法。

## 🔴 Controller 問題

### 9. 忘記做 Null Guard
**錯誤**：Controller/Handler 建構子未檢查 null。

**解決方案**：
```csharp
public CreateProductController(ICreateProductUseCase useCase)
{
    ArgumentNullException.ThrowIfNull(useCase);
    _useCase = useCase;
}
```

### 10. 非同步 Command 檢查 ExitCode
**錯誤**：Command 已排程仍檢查 ExitCode。

**解決方案**：直接回傳 `202 Accepted` 或結果物件，不需同步等待。

## 🔴 Testing 問題

### 11. 忘記呼叫 BDDfy()
**錯誤**：測試執行不觸發 Given/When/Then。

**解決方案**：
```csharp
[Fact]
public void Rule_Success_case()
{
    this.BDDfy();
}
```

### 12. 使用 BaseTestClass
**錯誤**：繼承 BaseTestClass/BaseUseCaseTest。

**解決方案**：改用 xUnit fixture + DI composition。

### 13. Profile 硬編碼在測試
**錯誤**：在 test code 內設定 `ASPNETCORE_ENVIRONMENT`。

**解決方案**：由 test runner / fixture 控制環境。

## 預防措施

1. 使用 Sub-agent Workflow
2. 參考 `.dev/standards/examples/`
3. 執行 `.ai/scripts/check-all.sh`
4. 查看 `.ai/CODE-REVIEW-INDEX.md`

最後更新：2026-02-01

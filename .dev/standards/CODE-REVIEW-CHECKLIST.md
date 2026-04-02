# 程式碼審查檢查清單 (.NET)

> 本檢查清單協助 AI 進行系統化 code review，確保 DDD/CA/CQRS 規範與品質一致。

## 📋 目錄
1. [通用檢查項目](#通用檢查項目)
2. [Domain 層檢查](#domain-層檢查)
3. [UseCase 層檢查](#usecase-層檢查)
4. [Adapter 層檢查](#adapter-層檢查)
5. [測試檢查](#測試檢查)
6. [效能檢查](#效能檢查)
7. [安全性檢查](#安全性檢查)
8. [文檔檢查](#文檔檢查)

## ✅ 通用檢查項目

### 🚨 避免過度設計 (YAGNI)
- [ ] **MUST**: 只實作 spec 檔案明確要求的功能
- [ ] **MUST**: Domain Events 與 spec 一對一對應
- [ ] **MUST**: 不預測未來需求，不實作「可能會用到」的功能
- [ ] **MUST**: 不因為範例有就照抄

### 編碼規範
- [ ] 遵循 C# 命名規範（類別 PascalCase、方法 camelCase）
- [ ] 無未使用的 `using`
- [ ] 無註解掉的程式碼
- [ ] 適當存取修飾符
- [ ] 遵循單一職責原則

### 程式碼品質
- [ ] 方法長度不超過 30 行（超過需拆分）
- [ ] 類別長度不超過 300 行
- [ ] 圈複雜度不超過 10
- [ ] 無重複程式碼

### 錯誤處理
- [ ] 適當的例外處理
- [ ] 不捕獲過於廣泛的例外
- [ ] 有意義的錯誤訊息
- [ ] 資源正確釋放（`using` / `await using`）

## 🏛️ Domain 層檢查

### 🚨 Event Sourcing 合規性檢查（最高優先級）

#### 🔴 Constructor 職責檢查
- [ ] **CRITICAL**: Constructor 不可直接設定狀態欄位（除集合初始化）
- [ ] **CRITICAL**: 事件必須透過 `Apply(event)` 觸發 `When(...)`
- [ ] **CRITICAL**: 狀態賦值僅出現在 `When(...)` 中

#### ✅ 正確模式
```csharp
public sealed class Product : AggregateRoot
{
    public Product(ProductId id, string name)
    {
        _tags = new List<Tag>();
        Apply(new ProductCreated(id.Value, name, DateProvider.Now()));
        Ensure("Product id set", () => _id.Value == id.Value);
    }

    private void When(ProductCreated e)
    {
        _id = new ProductId(e.ProductId);
        _name = e.Name;
    }
}
```

#### ❌ 反模式
```csharp
public Product(ProductId id, string name)
{
    _id = id; // ❌ 直接設定狀態
    _name = name;
    AddDomainEvent(new ProductCreated(...)); // ❌ 沒有 Apply
}
```

### 🚨 Semantics 語意合規性檢查
**重要**：檢查 `.dev/problem-frames/SEMANTICS.md` 與 `aggregate.yaml` 對應。

#### value_immutable
- [ ] 無 setter
- [ ] 無修改 event
- [ ] 只在 creation event 的 When 賦值

#### identity
- [ ] 必須同時具備 value_immutable
- [ ] 不存在修改 identity 的 use case/event

#### collection_reference_immutable
- [ ] 集合初始化一次，參考不可替換
- [ ] 僅透過 Aggregate 方法修改集合內容

#### soft_delete_flag
- [ ] 有對應 Deleted event
- [ ] 刪除後行為受限

#### optimistic_concurrency_version
- [ ] 版本由框架管理
- [ ] 禁止手動修改

### Aggregate 套件/目錄組織
- [ ] 每個 Aggregate 有獨立頂層資料夾/namespace
- [ ] Aggregate 只透過 ID 互相引用
- [ ] Value Object 不重複定義

### Contract / Require / Reject / Ensure
- [ ] `Require` 用於前置條件
- [ ] `Reject` 僅用於避免產生不必要事件
- [ ] `Ensure` 用於後置條件

## 🧩 UseCase 層檢查

### UseCase/Handler
- [ ] Handler 與對應 use case 名稱一致，能清楚表達這次 business operation
- [ ] Handler 可被視為 use case implementation，或明確委派給有實際價值的 Application Service
- [ ] 不為了名詞完整性硬多包一層只有單行轉呼叫的 `*UseCaseService`
- [ ] Handler 足夠薄，但仍完整承擔 application orchestration
- [ ] 不包含應放入 Aggregate 的 Domain 邏輯
- [ ] 使用 constructor injection
- [ ] 例外包裝為 UseCaseFailureException（若規範要求）

### Command / Query Boundary
- [ ] Command / Query 是 request model，不承載業務執行邏輯
- [ ] Command handler 處理狀態變更；Query handler 不改變 domain state
- [ ] Query handler 優先使用 query repository / query service，不把讀取流程拉回 aggregate
- [ ] 若抽出 Application Service，必須有明確 orchestration / reuse 價值

### Repository / Domain Service Usage
- [ ] Command side 透過 repository 載入與保存 aggregate
- [ ] Domain service 只承載真正無法歸屬於單一 aggregate 的 domain rule
- [ ] 沒有把 application orchestration 誤塞進 domain service

### Input/Output 設計
- [ ] Input/Output 為獨立 record/class
- [ ] Input/Output 只包含資料欄位
- [ ] DTO 放在 `src/Contracts` 或對應規範目錄

### Spec 對照檢查
- [ ] 建立 Spec 對照表
- [ ] 移除 spec 未要求的實作
- [ ] Domain Events 數量與 spec 一致

## 🔌 Adapter 層檢查

### Controller
- [ ] Controller 不包含業務邏輯
- [ ] 不直接操作 Repository
- [ ] 不直接操作 Aggregate
- [ ] 只負責把 protocol input 轉成 command / query，並把 result 轉回 response
- [ ] 同 BC 內若使用 bus / dispatcher 屬於 dispatch choice，不被誤當成 use case 本身
- [ ] 使用 ProblemDetails 統一錯誤格式

### Mapper
- [ ] Mapper 在 Application/Contracts 層級
- [ ] Mapper 為 static/sealed，禁止 DI
- [ ] 一個 DTO 對應一個 Mapper

### Projection / Inquiry
- [ ] 介面在 Application，實作在 Infrastructure
- [ ] 讀模型使用 EF Core Projection
- [ ] 不混入 Domain 行為

## 🧪 測試檢查

### BDD 規範
- [ ] 使用 xUnit + BDDfy（Gherkin 風格命名）
- [ ] 禁止 BaseTestClass
- [ ] Mock 使用 NSubstitute

### UseCase 測試 Given/When 規範
- [ ] Given/When 僅透過 UseCase
- [ ] 不直接操作 Aggregate

### 事件檢查
- [ ] 事件透過 MessageBus/Outbox 驗證
- [ ] 不直接檢查 Aggregate 內部事件列表

### 覆蓋率
- [ ] UseCase 100% 覆蓋
- [ ] Domain 邏輯 100% 覆蓋
- [ ] 錯誤與邊界情境有測試

## ⚡ 效能檢查
- [ ] 查詢使用 Projection
- [ ] 避免 N+1
- [ ] 批次操作優化

## 🔒 安全性檢查
- [ ] 所有輸入經驗證
- [ ] 防止注入/XSS
- [ ] 不記錄敏感資訊
- [ ] API 金鑰不寫死

## 📚 文檔檢查
- [ ] README/Spec 已更新
- [ ] 新功能有文檔
- [ ] Task 檔案更新（若流程要求）

## 🔄 Projection 實作檢查
- [ ] 產生 Projection Interface
- [ ] 產生 EF Core Implementation
- [ ] 使用 Mapper 轉換結果

## 🔗 相關資源
- `coding-standards.md`
- `USECASE-COMMAND-HANDLER-RELATIONSHIP.MD`
- `../guides/implementation-guides/COMMON-MISTAKES-GUIDE.md`
- `../guides/implementation-guides/TEMPLATE-USAGE-GUIDE.md`

# 測試編碼規範 (.NET)

本文件定義各層級測試的編碼標準，包含單元測試、Handler 測試、Controller 測試和整合測試。

---

## 📌 概述

測試必須遵循 xUnit + BDDfy（Gherkin 風格命名），並使用 NSubstitute 作為 mock 工具。

- **xUnit**：主要測試框架
- **BDDfy**：Handler / 整合測試必須使用 Gherkin 風格
- **NSubstitute**：唯一允許的 Mocking 框架
- **禁止 Moq**：專案不使用 Moq

---

## 🏷️ Pattern 標記（自動化檢查用）

以下標記供自動化 Code Review 腳本使用：

```yaml
# 測試框架規則
Pattern (forbidden, i): NUnit|MSTest|Moq|FakeItEasy|\[TestClass\]|\[TestMethod\]
Pattern (optional, any): BDDfy|TestStack\.BDDfy|Gherkin-style

# Mock 規則
Pattern (optional, any): Substitute\.For

# 禁止 BaseTestClass
Pattern (forbidden, ignore-comment): BaseTestClass|BaseUseCaseTest
```

---

## 🔴 必須遵守的規則 (MUST FOLLOW)

### 1. 測試框架選擇

| 測試類型 | 框架 | 說明 |
|---------|------|------|
| 單元測試 | xUnit + BDDfy | Gherkin-style 命名 |
| 整合測試 | xUnit + WebApplicationFactory | ASP.NET Core 整合測試 |
| Mocking | NSubstitute | **禁止使用 Moq** |
| 斷言 | FluentAssertions | 推薦使用 |

---

### 2. 禁止使用 BaseTestClass

**強制規定**: 測試類別必須是獨立的，不能繼承任何基底測試類別。

```csharp
// ❌ 錯誤：使用 BaseTestClass
public class CreateProductHandlerTests : BaseTestClass
{
    // FORBIDDEN!
}

// ❌ 錯誤：使用共用基底類別
public class CreateProductHandlerTests : IntegrationTestBase
{
    // FORBIDDEN!
}

// ✅ 正確：獨立的測試類別
public class CreateProductHandlerTests
{
    private readonly IRepository<Product, ProductId> _repository;
    private readonly CreateProductHandler _handler;
    
    public CreateProductHandlerTests()
    {
        _repository = Substitute.For<IRepository<Product, ProductId>>();
        _handler = new CreateProductHandler(_repository, ...);
    }
}
```

---

### 3. 使用 BDDfy 與 Gherkin-Style 命名

**強制規定**: Handler 和整合測試必須使用 BDDfy 與 Gherkin-style 命名。

```csharp
// ✅ 正確：BDDfy + Gherkin-style
public class CreateProductHandlerTests
{
    private CreateProductCommand _command = null!;
    private Result<ProductId> _result = null!;
    private readonly IRepository<Product, ProductId> _repository;
    private readonly CreateProductHandler _handler;

    public CreateProductHandlerTests()
    {
        _repository = Substitute.For<IRepository<Product, ProductId>>();
        var unitOfWork = Substitute.For<IUnitOfWork>();
        var logger = Substitute.For<ILogger<CreateProductHandler>>();
        _handler = new CreateProductHandler(_repository, unitOfWork, logger);
    }

    [Fact]
    public void Should_create_product_successfully_when_input_is_valid()
    {
        this.Given(x => x.GivenAValidProductCreationCommand())
            .When(x => x.WhenTheHandlerIsExecuted())
            .Then(x => x.ThenTheProductShouldBeCreated())
            .And(x => x.ThenTheResultShouldBeSuccess())
            .BDDfy();
    }

    private void GivenAValidProductCreationCommand()
    {
        _command = new CreateProductCommand(
            Guid.NewGuid().ToString(),
            "Test Product",
            "user-123"
        );
    }

    private async Task WhenTheHandlerIsExecuted()
    {
        _result = await _handler.Handle(_command, CancellationToken.None);
    }

    private void ThenTheProductShouldBeCreated()
    {
        _repository.Received(1).SaveAsync(Arg.Any<Product>(), Arg.Any<CancellationToken>());
    }

    private void ThenTheResultShouldBeSuccess()
    {
        _result.IsSuccess.Should().BeTrue();
        _result.Value.Should().NotBeNull();
    }
}

// ❌ 錯誤：純 AAA 風格（Handler 測試禁止）
[Fact]
public async Task TestCreateProduct()  // 錯誤命名
{
    // Arrange
    var command = new CreateProductCommand(...);
    
    // Act
    var result = await _handler.Handle(command, CancellationToken.None);
    
    // Assert
    Assert.True(result.IsSuccess);  // 沒有 BDDfy
}
```

---

### 4. 測試資料 ID 規範

**強制規定**: 所有聚合根 ID 必須使用 `Guid.NewGuid().ToString()` 來避免測試間的 ID 衝突。

```csharp
// ✅ 正確：使用 Guid 產生唯一 ID
private void GivenAValidCommand()
{
    _command = new CreateProductCommand(
        Guid.NewGuid().ToString(),  // ✅ 使用 Guid
        "Test Product",
        "user-123"  // userId 可以用固定字串
    );
}

// ❌ 錯誤：使用固定的 ID
private void GivenAValidCommand()
{
    _command = new CreateProductCommand(
        "product-1",  // ❌ 固定 ID 會造成重複
        "Test Product",
        "user-123"
    );
}
```

**例外規則**: `userId` 和 `creatorId` 可以使用固定字串，因為它們不是聚合根 ID。

---

### 5. Contract Tests 用於 DBC 驗證

**強制規定**: Aggregate 的前置條件必須有對應的 Contract Tests。

```csharp
// ✅ 正確：Contract Test 使用純 xUnit
public class ProductContractTests
{
    [Fact]
    public void Rename_Throws_WhenNameIsNull()
    {
        // Arrange
        var product = CreateProductWithState(ProductState.Active);
        
        // Act & Assert
        Assert.Throws<ArgumentNullException>(() => product.Rename(null!));
    }
    
    [Fact]
    public void Rename_Throws_WhenProductIsDeleted()
    {
        // Arrange
        var product = CreateProductWithState(ProductState.Deleted);
        
        // Act & Assert
        var ex = Assert.Throws<InvalidOperationException>(
            () => product.Rename("New Name"));
        Assert.Contains("deleted", ex.Message.ToLower());
    }
    
    private static Product CreateProductWithState(ProductState state)
    {
        var product = new Product(ProductId.Create(), "Test");
        // Set state via internal method or reflection
        return product;
    }
}

// ❌ 錯誤：使用 try-catch
[Fact]
public void Rename_Throws_WhenNameIsNull()
{
    try
    {
        product.Rename(null!);
        Assert.Fail("Expected exception");  // FORBIDDEN!
    }
    catch (ArgumentNullException) { }
}
```

---

### 6. 使用 NSubstitute（禁止 Moq）

**強制規定**: 必須使用 NSubstitute 進行 mocking，禁止使用 Moq。

```csharp
// ✅ 正確：NSubstitute
var repository = Substitute.For<IRepository<Product, ProductId>>();
repository.FindByIdAsync(Arg.Any<ProductId>(), Arg.Any<CancellationToken>())
    .Returns(Task.FromResult<Product?>(existingProduct));

// 驗證呼叫
await repository.Received(1).SaveAsync(Arg.Any<Product>(), Arg.Any<CancellationToken>());

// ❌ 錯誤：Moq
var repository = new Mock<IRepository<Product, ProductId>>();  // FORBIDDEN!
repository.Setup(x => x.FindByIdAsync(...)).ReturnsAsync(existingProduct);
repository.Verify(x => x.SaveAsync(...), Times.Once);
```

---

## 🎯 測試分層策略

### 測試金字塔

```
         /\
        /E2E\      <- 最少 (5%)
       /------\
      /  整合  \    <- 適中 (20%)
     /----------\
    / Controller \  <- 較多 (25%)
   /--------------\
  /   Handler     \ <- 多 (25%)
 /------------------\
/    單元測試        \ <- 最多 (25%)
----------------------
```

### 各層測試職責

| 層級 | 測試內容 | 測試框架 | Mock 策略 |
|------|---------|---------|---------
| Unit Test | Domain logic, Value Objects | xUnit | No mocks |
| Handler Test | Business flow | xUnit + BDDfy | Mock Repository |
| Controller Test | HTTP behavior | WebApplicationFactory | Mock Handler |
| Integration Test | Database, External API | xUnit | Real dependencies |
| E2E Test | Complete user journey | Playwright | No mocks |

---

## 🎯 測試命名規範

### 命名模式

```csharp
// Pattern: Should_[expected_result]_when_[condition]

// ✅ 好的命名
Should_create_product_successfully_when_input_is_valid()
Should_throw_exception_when_name_is_null()
Should_return_404_when_product_not_found()

// ❌ 不好的命名
TestCreateProduct()  // 太籠統
Test1()              // 無意義
CreateProductTest()  // 沒有說明預期結果
```

### BDDfy 步驟命名

```csharp
// ✅ 好的步驟名稱
private void GivenAValidProductCreationCommand() { }
private void GivenAnExistingProduct() { }
private async Task WhenTheHandlerIsExecuted() { }
private void ThenTheProductShouldBeCreated() { }
private void ThenTheResultShouldBeSuccess() { }

// ❌ 不好的步驟名稱
private void Setup() { }
private void DoTest() { }
private void Check() { }
```

---

## 🎯 測試資料建構

### Test Data Builder Pattern

```csharp
public class ProductBuilder
{
    private ProductId _id = ProductId.Create();
    private string _name = "Default Product";
    private string _creatorId = "user-123";
    private ProductState _state = ProductState.Active;

    public static ProductBuilder AProduct() => new();

    public ProductBuilder WithId(ProductId id)
    {
        _id = id;
        return this;
    }

    public ProductBuilder WithName(string name)
    {
        _name = name;
        return this;
    }

    public ProductBuilder WithState(ProductState state)
    {
        _state = state;
        return this;
    }

    public Product Build()
    {
        var product = new Product(_id, _name, _creatorId);
        // Set state if needed
        return product;
    }
}

// 使用
var product = ProductBuilder.AProduct()
    .WithName("Custom Product")
    .WithState(ProductState.Deleted)
    .Build();
```

---

## 🔍 檢查清單

### Handler 測試
- [ ] 使用 BDDfy + Gherkin-style 命名
- [ ] 使用 NSubstitute（不是 Moq）
- [ ] 沒有繼承 BaseTestClass
- [ ] 聚合根 ID 使用 `Guid.NewGuid().ToString()`
- [ ] 命名符合 `Should_xxx_when_xxx` 模式

### Contract 測試
- [ ] 使用純 xUnit（無 BDDfy）
- [ ] 使用 `Assert.Throws<TException>()`
- [ ] 有 `CreateProductWithState()` helper
- [ ] 每個前置條件都有對應測試

### Controller 測試
- [ ] 使用 WebApplicationFactory
- [ ] Mock Handler 而非 Repository
- [ ] 驗證 HTTP Status Code
- [ ] 驗證 Response Body

---

## 📂 程式碼範例

更多完整範例請參考：

| 範例 | 路徑 |
|------|------|
| BDD Gherkin 測試 | [../examples/bdd-gherkin-test/](../examples/bdd-gherkin-test/) |
| BDD Given-When-Then | [../examples/bdd-given-when-then-example/](../examples/bdd-given-when-then-example/) |
| UseCase 測試範例 | [../examples/use-case-test-example.md](../examples/use-case-test-example.md) |
| 測試指南 | [../examples/testing-guide.md](../examples/testing-guide.md) |

---

## 相關文件

- [aggregate-standards.md](aggregate-standards.md)
- [usecase-standards.md](usecase-standards.md)
- [controller-standards.md](controller-standards.md)

> generate by gemini cli, model: gemini-2.5 pro

# Order api / Product api 中的 command handler 做法比較

## 模式一：Orders 的做法 - 指令與處理器合一 (Self-Contained Command)

這種模式將一個 Command 和它對應的 Handler 放在同一個檔案中。

- PlaceOrderCommand.cs
    ```csharp
    // 1. Command 的定義
    public record PlaceOrderCommand(...);

    // 2. 對應的 Handler 也在同一個檔案
    public class PlaceOrderCommandHandler
    {
        public static async Task<Guid> HandleAsync(PlaceOrderCommand command, ...)
         {
             // ... 處理邏輯
         }
    }
    ```

### 核心特點

* 高內聚性 (High Cohesion)：一個「用例 (Use Case)」或「功能 (Feature)」的所有相關邏輯（指令定義、處理過程）都集中在單一檔案中。
* 關注點分離: 檔案本身就是一個功能單元。當你想了解「下單」這個功能時，只需要打開 PlaceOrderCommand.cs 這一個檔案。
* 依賴注入: 依賴項（如 IOrderDomainRepository）是直接注入到 HandleAsync 方法中的。這通常是 WolverineFx 這類現代框架的特性，它能自動解析方法參數的依賴。

### 適用情境

* 複雜或獨特的指令：當一個指令的處理邏輯非常獨特，與其他指令幾乎沒有共享的程式碼時，這種模式非常理想。例如，「下單」可能涉及到呼叫庫存、計算折扣、產生發 票等多個步驟，而「取消訂單」的邏輯則完全不同。
* 功能導向的團隊分工：當開發人員是按功能（Feature）而不是按技術層（Layer）來劃分工作時，這種方式更容易協作，減少合併衝突。
* 追求極致的單一職責原則 (SRP)：每個檔案只負責一個非常具體的 use case。

---

## 模式二：Products 的做法 - 集中式處理器 (Centralized Handler)

這種模式將多個相關的 Command 分別定義在各自的檔案中，然後用一個統一的 Handler 類別來處理針對同一個「聚合根 (Aggregate Root)」的所有操作。

- CreateProductCommand.cs
    ```csharp
    public record CreateProductCommand(...);
    ```
- UpdateProductCommand.cs
    ```csharp
    public record UpdateProductCommand(...);
    ```
- ProductHandler.cs
    ```csharp
    public class ProductHandler
    {
         // 處理 Create
         public static async Task<ProductDto> Handle(CreateProductCommand command, ...) { ... }

        // 處理 Update
        public static async Task Handle(UpdateProductCommand command, ...) { ... }

        // 處理 Delete
        public static async Task Handle(DeleteProductCommand command, ...) { ... }

        // 同時也處理 Query (這是一種變體，有時 Query 會被分離到另一個 Handler)
        public static async Task<IEnumerable<ProductDto>> Handle(GetAllProductsQuery query, ...) { ... }
    }
    ```

### 核心特點

* 聚合根導向 (Aggregate-Oriented)：ProductHandler 集中了所有與 Product 這個聚合根相關的 CUD (Create, Update, Delete) 操作。這讓你對 Product 能做什麼一目了然。
* 共享依賴和邏輯：如果多個指令處理需要共享相同的依賴（例如 IProductDomainRepository），或者有可以重用的私有輔助方法（例如 private async Task<Product> FindProductOrFailAsync(...)），這種模式更容易實作。依賴可以注入到 Handler 的建構子中（雖然此範例用的是靜態方法注入，但建構子注入是更常見的用法）。
* 檔案數量較少：對於一個擁有很多操作的聚合根，可以避免產生大量細碎的 Handler 檔案。

### 適用情境

* CRUD-heavy 的聚合根：當一個聚合根有大量標準的、相似的 CRUD 操作時，這種方式非常高效，可以減少大量重複的程式碼。Product 就是一個典型的例子。
* 需要共享邏輯：當不同指令的處理過程中有共同的步驟時（例如，每個操作前都需要先驗證產品是否存在），可以將這些步驟抽取成 Handler 內的私有方法。
* 簡化依賴管理：當所有方法共享同一組依賴時，透過建構子注入一次即可，讓 Handle 方法的簽名更簡潔。

## 核心差異總結

| 特性    | Orders (指令與處理器合一)   | Products (集中式處理器)      |
|-------|---------------------|------------------------|
| 組織方式  | 以「功能/用例」為中心         | 以「聚合根/實體」為中心           |
| 檔案結構  | 一個檔案 = 一個功能         | 一個 Handler 處理多個功能      |
| 內聚性   | 功能內聚性高              | 聚合根操作內聚性高              |
| 程式碼重用 | 較難在不同 Handler 間共享邏輯 | 容易在 Handler 內部共享邏輯     |
| 最適用途  | 複雜、獨特的指令            | CRUD 密集、邏輯相似的指令集       |
| 潛在風險  | 若指令過多，可能導致檔案數量暴增    | 若聚合根操作過多，Handler 可能變臃腫 |

## 結論與建議

這兩種模式都是業界認可的有效方法，沒有絕對的優劣，只有是否適合當前的業務情境。

* Orders 的做法更貼近 "Feature Slices" 或 "Vertical Slice Architecture" 的思想。
* Products 的做法是更傳統的、按聚合根職責劃分的 Handler 模式。

為了專案的長期可維護性，建議團隊選擇一種主要風格來遵循。

* 如果專案中的多數業務邏輯都像 Product 一樣是 CRUD 密集型的，那麼集中式處理器可能是更高效的選擇。
* 如果專案的業務邏輯多數像 Order 一樣，每個操作都非常獨特且複雜，那麼指令與處理器合一的模式會更清晰。
# gemini cli gen history

> 使用 gemini cli & gemini 2.5 pro 執行 spec-kit 的語法後的對話紀錄

```terminaloutput
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│  > /specify Product Consumer 要接收 OrderCancelled 事件，並且將該訂單內紀錄的產品以及購買數量回填至產品庫存中  │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

✦ 好的，我將執行腳本以從功能描述創建新的功能規格。
╭───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ✓  Shell .\specify\scripts\powershell\create-new-feature.ps1 -Json "Product Consumer 要接收 OrderCancelled 事件，並且將該訂單內紀錄的產品以及購買數量回…  │
│                                                                                                                                                           │
│    The system cannot find the path specified.                                                                                                             │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
✦ 腳本執行失敗，因為找不到指定的路徑。我將確認 .specify/scripts/powershell/ 目錄是否存在，然後重試。
╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ✓  ReadFolder .specify\scripts\powershell                                                                                                       │
│                                                                                                                                                 │
│    Listed 6 item(s).                                                                                                                            │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
✦ 好的，目錄和檔案都存在。我將透過 powershell.exe 明確地調用腳本來重試執行，這應該可以解決之前的問題。
╭───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ✓  Shell powershell.exe -File .\.specify\scripts\powershell\create-new-feature.ps1 -Json "Product Consumer 要接收 OrderCancelled 事件，並且將該訂單內紀…  │
│                                                                                                                                                           │
│    {"BRANCH_NAME":"003-product-consumer-ordercancelled","SPEC_FILE":"C:\\Github\\YuChia\\dotnet-mq-arch-lab\\specs\\003-product-consumer-order            │
│
│    Switched to a new branch '003-product-consumer-ordercancelled'                                                                                         │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
✦ 腳本執行成功。

- 分支名稱: 003-product-consumer-ordercancelled
- 規格檔案路徑: C:\Github\YuChia\dotnet-mq-arch-lab\specs\003-product-consumer-ordercancelled\spec.md


我現在將根據功能描述，使用範本來填寫規格檔案的內容。
╭──────────────────────────────────────────────────╮
│ ✓  ReadFile .specify\templates\spec-template.md  │
╰──────────────────────────────────────────────────╯
✦ 好的，我會用範本內容建立新的規格檔案，並寫入 SPEC_FILE。
╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ✓  WriteFile Writing to specs\\spec.md                                                                                                          │
│                                                                                                                                                 │
│     1 # Feature Specification: Product Stock Restoration on Order Cancellation                                                                  │
│     2                                                                                                                                           │
│     3 **Feature Branch**: `003-product-consumer-ordercancelled`                                                                                 │
│     4 **Created**: 2025-09-18                                                                                                                   │
│     5 **Status**: Draft                                                                                                                         │
│     6 **Input**: User description: "Product Consumer 要接收 OrderCancelled 事件，並且將該訂單內紀錄的產品以及購買數量回填至產品庫存中"          │
│     7                                                                                                                                           │
│     8 ---                                                                                                                                       │
│     9                                                                                                                                           │
│    10 ## ⚡ Quick Guidelines                                                                                                                    │
│    11 - ✅ Focus on WHAT users need and WHY                                                                                                     │
│    12 - ❌ Avoid HOW to implement (no tech stack, APIs, code structure)                                                                         │
│    13 - 👥 Written for business stakeholders, not developers                                                                                    │
│    14                                                                                                                                           │
│    15 ---                                                                                                                                       │
│    16                                                                                                                                           │
│    17 ## User Scenarios & Testing *(mandatory)*                                                                                                 │
│    18                                                                                                                                           │
│    19 ### Primary User Story                                                                                                                    │
│    20 As the inventory system, when an order is cancelled, I need to automatically process an `OrderCancelled` event to return the products     │
│       from that order back into the available stock. This ensures that inventory levels are accurate and cancelled items can be purchased by    │
│       other customers.                                                                                                                          │
│    21                                                                                                                                           │
│    22 ### Acceptance Scenarios                                                                                                                  │
│    23 1. **Given** a product "P1" has a stock level of 50 units, **When** an `OrderCancelled` event is received for an order that contained 5   │
│       units of "P1", **Then** the stock level of product "P1" MUST be updated to 55 units.                                                      │
│    24 2. **Given** the system successfully processes an `OrderCancelled` event with a unique identifier, **When** the same event is received    │
│       again, **Then** the system MUST NOT add the product quantities to the stock again, ensuring the operation is idempotent.                  │
│    25                                                                                                                                           │
│    26 ### Edge Cases                                                                                                                            │
│    27 - **What happens when** the `OrderCancelled` event contains a Product ID that does not exist?                                             │
│    28   - The system should log this as a warning and continue processing other products in the event without failing.                          │
│    29 - **How does the system handle** a negative or zero quantity for a product in the event?                                                  │
│    30   - The item should be skipped, logged as an invalid data entry, and the process should continue.                                         │
│    31                                                                                                                                           │
│    32 ## Requirements *(mandatory)*                                                                                                             │
│    33                                                                                                                                           │
│    34 ### Functional Requirements                                                                                                               │
│    35 - **FR-001**: The Product service/consumer MUST subscribe to and consume the `OrderCancelled` integration event.                          │
│    36 - **FR-002**: Upon receiving an `OrderCancelled` event, the system MUST parse the event to extract the list of products, including each   │
│       product's ID and the quantity to be restocked.                                                                                            │
│    37 - **FR-003**: For each valid product in the event, the system MUST increase the corresponding product's stock quantity by the amount      │
│       specified in the event.                                                                                                                   │
│    38 - **FR-004**: The event processing logic MUST be idempotent. If the same `OrderCancelled` event is processed multiple times, the stock    │
│       restoration must only occur once.                                                                                                         │
│    39 - **FR-005**: The system MUST log the outcome of each stock restoration attempt (e.g., success, warning for non-existent product, or      │
│       failure).                                                                                                                                 │
│    40                                                                                                                                           │
│    41 ### Key Entities *(include if feature involves data)*                                                                                     │
│    42 - **Product**: Represents an item for sale. Key attributes include `ProductId` and `StockQuantity`.                                       │
│    43 - **OrderCancelled Event**: An integration event indicating an order has been cancelled. Its payload contains a list of items, where      │
│       each item has a `ProductId` and `Quantity`.                                                                                               │
│    44                                                                                                                                           │
│    45 ---                                                                                                                                       │
│    46                                                                                                                                           │
│    47 ## Review & Acceptance Checklist                                                                                                          │
│    48 *GATE: To be checked before moving to the planning phase.*                                                                                │
│    49                                                                                                                                           │
│    50 ### Content Quality                                                                                                                       │
│    51 - [X] No implementation details (languages, frameworks, APIs)                                                                             │
│    52 - [X] Focused on user value and business needs                                                                                            │
│    53 - [X] Written for non-technical stakeholders                                                                                              │
│    54 - [X] All mandatory sections completed                                                                                                    │
│    55                                                                                                                                           │
│    56 ### Requirement Completeness                                                                                                              │
│    57 - [X] No [NEEDS CLARIFICATION] markers remain                                                                                             │
│    58 - [X] Requirements are testable and unambiguous                                                                                           │
│    59 - [X] Success criteria are measurable                                                                                                     │
│    60 - [X] Scope is clearly bounded                                                                                                            │
│    61 - [X] Dependencies and assumptions identified                                                                                             │
│    62                                                                                                                                           │
│    63 ---                                                                                                                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
✦ 功能規格已成功建立。


- 功能分支: 003-product-consumer-ordercancelled
  現在已準備好進入下一階段：規劃 (/plan 指令)。

╭───────────╮
│  > /plan  │
╰───────────╯

✦ 好的，我將開始執行實作規劃流程。
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ✓  Shell powershell.exe -File .\.specify\scripts\powershell\setup-plan.ps1 -Json (Set up the implementation plan for the current feature branch.)  │
│                                                                                                                                                    │
│    {"FEATURE_SPEC":"C:\\Github\\YuChia\\dotnet-mq-arch-lab\\specs\\003-product-consumer-ordercancelled\\spec.md","IMPL_PLAN":"C:\\Github\\YuCh     │
│    ia\\dotnet-mq-arch-lab\\specs\\003-product-consumer-ordercancelled\\plan.md","SPECS_DIR":"C:\\Github\\YuChia\\dotnet-mq-arch-lab\\specs\\00     │
│    3-product-consumer-ordercancelled","BRANCH":"003-product-consumer-ordercancelled"}                                                              │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
✦ 計畫設置成功。我已獲得所有必要的路徑和分支名稱。


- 功能規格: C:\Github\YuChia\dotnet-mq-arch-lab\specs\003-product-consumer-ordercancelled\spec.md
  接下來，我將讀取功能規格、章程和計畫範本，以開始產生設計產物。
  ╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
  │ ✓  ReadFile specs\\spec.md                                                                                                                      │
  │                                                                                                                                                 │
  │ ✓  ReadFile .specify\memory\constitution.md                                                                                                     │
  │                                                                                                                                                 │
  │ x  ReadFile {"absolute_path":"C:\\Github\\YuChia\\dotnet-mq-arch-lab\\specs\\003-product-consumer-ordercancelled\\plan.md"}                     │
  │                                                                                                                                                 │
  │    File not found: C:\Github\YuChia\dotnet-mq-arch-lab\specs\003-product-consumer-ordercancelled\plan.md                                        │
  │                                                                                                                                                 │
  │ ✓  FindFiles '**/OrderCancelled.cs'                                                                                                             │
  │                                                                                                                                                 │
  │    Found 2 matching file(s)                                                                                                                     │
  ╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
  ✦ 我已閱讀功能規格與章程。plan.md 未找到是預料中的，因為 setup-plan.ps1 腳本僅建立了目錄。我將使用記憶中的 plan-template.md 內容來建立 plan.md。


glob 找到了兩個 OrderCancelled.cs 檔案，我將讀取原始碼中官方的合約檔案 (src/BC-Contracts/...) 來了解其結構。


接下來，我將讀取該合約，產生 plan.md、research.md、data-model.md 和 quickstart.md 的內容，將這四個檔案寫入 specs/003-product-consumer-ordercancelled/
目錄，然後報告完成。
╭─────────────────────────────────────╮
│ ✓  ReadFile src\\OrderCancelled.cs  │
╰─────────────────────────────────────╯
✦ 我發現 OrderCancelled.cs 事件只包含 OrderId，沒有產品列表。這表示 Product.Consumer 必須查詢 SaleOrders.WebApi 以獲取訂單詳情，這增加了實作的複雜性。


我的計畫是：
1.  在 research.md 中記錄此發現以及查詢 API 的決定。
2.  在 data-model.md 中定義 SaleOrders.WebApi 預期回傳的 DTO。
3.  更新 quickstart.md，將 SaleOrders.WebApi 加入為必要的前置步驟。
4.  更新 plan.md 的技術背景和任務規劃，以反映新的 API 呼叫需求。


我現在將產生並寫入這四個設計產物。
╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ✓  WriteFile Writing to specs\\plan.md                                                                                                          │
│                                                                                                                                                 │
│    ... first 80 lines hidden ...                                                                                                                │
│     81 ## Phase 3+: Future Implementation                                                                                                       │
│     82 *These phases are beyond the scope of the /plan command*                                                                                 │
│     83                                                                                                                                          │
│     84 ## Complexity Tracking                                                                                                                   │
│     85 | Violation | Why Needed | Simpler Alternative Rejected Because |                                                                        │
│     86 |---|---|---|                                                                                                                            │
│     87 | Cross-service communication (API call) | The `OrderCancelled` event lacks product details. The Product context needs this data to      │
│        perform its function. | Enriching the event was rejected to keep event payloads small. A shared database was rejected as it violates     │
│        bounded context autonomy. |                                                                                                              │
│     88                                                                                                                                          │
│     89 ## Progress Tracking                                                                                                                     │
│     90 - [X] Phase 0: Research complete                                                                                                         │
│     91 - [X] Phase 1: Design complete                                                                                                           │
│     92 - [X] Phase 2: Task planning approach described                                                                                          │
│     93 - [ ] Phase 3: Tasks generated (/tasks command)                                                                                          │
│     94 - [ ] Phase 4: Implementation complete                                                                                                   │
│     95 - [ ] Phase 5: Validation passed                                                                                                         │
│     96                                                                                                                                          │
│     97 **Gate Status**:                                                                                                                         │
│     98 - [X] Initial Constitution Check: PASS                                                                                                   │
│     99 - [X] Post-Design Constitution Check: PASS                                                                                               │
│    100 - [X] All NEEDS CLARIFICATION resolved                                                                                                   │
│    101 - [X] Complexity deviations documented                                                                                                   │
│    102                                                                                                                                          │
│    103 ---                                                                                                                                      │
│    104 *Based on project guidelines in AGENTS.md*                                                                                               │
│                                                                                                                                                 │
│ ✓  WriteFile Writing to specs\\research.md                                                                                                      │
│                                                                                                                                                 │
│    ... first 15 lines hidden ...                                                                                                                │
│    14 ```                                                                                                                                       │
 │    15                                                                                                                                           │
 │    16 This means the `Product.Consumer` does not have enough information to fulfill its requirement of restocking products.                     │
 │    17                                                                                                                                           │
 │    18 ### Decision                                                                                                                              │
 │    19 The `Product.Consumer` service will make a synchronous API call to the `SaleOrders.WebApi` to fetch the required product details for the  │
 │       given `OrderId`.                                                                                                                          │
 │    20                                                                                                                                           │
 │    21 This requires a new endpoint to be created in `SaleOrders.WebApi` that can expose these details.                                          │
 │    22                                                                                                                                           │
 │    23 ### Rationale                                                                                                                             │
 │    24 This approach is chosen for the following reasons:                                                                                        │
 │    25 1.  **Respects Bounded Contexts**: It avoids direct database dependencies between the `Product` and `Order` services. Each service        │
 │       remains the single source of truth for its own data, which is a core principle of Domain-Driven Design and Clean Architecture.            │
 │    26 2.  **Avoids Event Bloat**: While the `OrderCancelled` event could be enriched with product details, this would make the event payload    │
 │       significantly larger. Not all potential subscribers to this event may need the product list, so keeping the event lean is preferable.     │
 │    27 3.  **Standard Microservice Pattern**: A service consuming an event and then calling back to another service for more data (a pattern     │
 │       sometimes called "Query back") is a common and acceptable pattern in microservice architectures when dealing with data owned by another   │
 │       service.                                                                                                                                  │
 │    28                                                                                                                                           │
 │    29 ### Alternatives Considered                                                                                                               │
 │    30 -   **Enriching the `OrderCancelled` Event**: This would involve adding the list of products and quantities directly to the event         │
 │       payload. This was rejected to maintain a lean event message and avoid coupling the event structure too tightly to the needs of one        │
 │       specific consumer.                                                                                                                        │
 │    31 -   **Shared Database/View**: This would involve creating a database view or table that both services could access. This was rejected as  │
 │       it creates strong data-level coupling and violates the principle of each bounded context owning its own data.                             │
 │                                                                                                                                                 │
 │ ✓  WriteFile Writing to specs\\data-model.md                                                                                                    │
 │                                                                                                                                                 │
 │    ... first 16 lines hidden ...                                                                                                                │
 │    17 To facilitate the communication between the `Product.Consumer` and the `SaleOrders.WebApi`, a new Data Transfer Object (DTO) is           │
 │       required. This DTO will be the contract for the API call that retrieves order details.                                                    │
 │    18                                                                                                                                           │
 │    19 ### OrderDetailsResponse DTO                                                                                                              │
 │    20                                                                                                                                           │
 │    21 This DTO will be defined in a shared `BC-Contracts` project to be referenced by both the `SaleOrders.WebApi` (as an output) and the       │
 │       `Product` context (as an input).                                                                                                          │
 │    22                                                                                                                                           │
 │    23 -   **Namespace**: `Lab.MessageSchemas.Orders.DataTransferObjects`                                                                        │
 │    24 -   **File**: `OrderDetailsResponse.cs`                                                                                                   │
 │    25                                                                                                                                           │
 │    26 ```csharp                                                                                                                                 │
│    27 namespace Lab.MessageSchemas.Orders.DataTransferObjects;                                                                                  │
│    28                                                                                                                                           │
│    29 public record OrderDetailsResponse                                                                                                        │
│    30 {                                                                                                                                         │
│    31     public Guid OrderId { get; init; }                                                                                                    │
│    32     public List<LineItemDto> LineItems { get; init; } = new();                                                                            │
│    33 }                                                                                                                                         │
│    34                                                                                                                                           │
│    35 public record LineItemDto                                                                                                                 │
│    36 {                                                                                                                                         │
│    37     public Guid ProductId { get; init; }                                                                                                  │
│    38     public int Quantity { get; init; }                                                                                                    │
│    39 }                                                                                                                                         │
│    40 ```                                                                                                                                       │
 │                                                                                                                                                 │
 │ ✓  WriteFile Writing to specs\\quickstart.md                                                                                                    │
 │                                                                                                                                                 │
 │    ... first 44 lines hidden ...                                                                                                                │
 │    45     ```                                                                                                                                   │
│    46 2.  Note the `orderId` returned in the response.                                                                                          │
│    47                                                                                                                                           │
│    48 ### Step 3: Cancel the Sales Order                                                                                                        │
│    49                                                                                                                                           │
│    50 1.  Cancel the order you just created. This action will publish the `OrderCancelled` integration event.                                   │
│    51                                                                                                                                           │
│    52     **Example Request:**                                                                                                                  │
│    53     ```http                                                                                                                               │
 │    54     DELETE http://localhost:5002/api/orders/{your-order-id}                                                                               │
 │    55     ```                                                                                                                                   │
│    56                                                                                                                                           │
│    57 ### Step 4: Verify Stock Restoration                                                                                                      │
│    58                                                                                                                                           │
│    59 1.  Wait a few moments for the `SaleProducts.Consumer` to process the `OrderCancelled` event.                                             │
│    60 2.  Query the product's details again.                                                                                                    │
│    61                                                                                                                                           │
│    62     **Example Request:**                                                                                                                  │
│    63     ```http                                                                                                                               │
 │    64     GET http://localhost:5001/api/products/{your-product-id}                                                                              │
 │    65     ```                                                                                                                                   │
│    66                                                                                                                                           │
│    67 ### Expected Result                                                                                                                       │
│    68                                                                                                                                           │
│    69 The `stock` level of the product should now be restored to its original value from Step 1. If the stock was 50 and the cancelled order    │
│       contained 2 items, the stock should be 50 again.                                                                                          │
│                                                                                                                                                 │
│ ✓  WriteFile Writing to ...pecs\contracts\OrderDetailsResponse.cs                                                                               │
│                                                                                                                                                 │
│     1 namespace Lab.MessageSchemas.Orders.DataTransferObjects;                                                                                  │
│     2                                                                                                                                           │
│     3 public record OrderDetailsResponse                                                                                                        │
│     4 {                                                                                                                                         │
│     5     public Guid OrderId { get; init; }                                                                                                    │
│     6     public List<LineItemDto> LineItems { get; init; } = new();                                                                            │
│     7 }                                                                                                                                         │
│     8                                                                                                                                           │
│     9 public record LineItemDto                                                                                                                 │
│    10 {                                                                                                                                         │
│    11     public Guid ProductId { get; init; }                                                                                                  │
│    12     public int Quantity { get; init; }                                                                                                    │
│    13 }                                                                                                                                         │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
✦ 實作規劃階段已完成。


- 分支名稱: 003-product-consumer-ordercancelled
  此功能現在已準備好進入任務產生階段 (/tasks 指令)。


╭────────────╮
│  > /tasks  │
╰────────────╯

✦ 好的，我將開始產生 tasks.md 檔案。
╭───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ✓  Shell powershell.exe -File .\.specify\scripts\powershell\check-task-prerequisites.ps1 -Json (Check for available design documents for the current fe…  │
│                                                                                                                                                           │
│    {"FEATURE_DIR":"C:\\Github\\YuChia\\dotnet-mq-arch-lab\\specs\\003-product-consumer-ordercancelled","AVAILABLE_DOCS":["research.md","data-m            │
│    odel.md","contracts/","quickstart.md"]}                                                                                                                │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
✦ 好的，我將產生 tasks.md。我已確認必要文件，現在將讀取 plan.md、research.md、data-model.md、quickstart.md 及合約檔案，然後根據分析產生 tasks.md
內容，寫入功能目錄後報告完成。
╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ✓  ReadManyFiles Will attempt to read and concatenate files using patterns:                                                                     │
│    …                                                                                                                                            │
│                                                                                                                                                 │
│    ### ReadManyFiles Result (Target Dir: `C:\Github\YuChia\dotnet-mq-arch-lab`)                                                                 │
│                                                                                                                                                 │
│    Successfully read and concatenated content from **5 file(s)**.                                                                               │
│                                                                                                                                                 │
│    **Processed Files:**                                                                                                                         │
│    - `specs/003-product-consumer-ordercancelled/contracts/OrderDetailsResponse.cs`                                                              │
│    - `specs/003-product-consumer-ordercancelled/data-model.md`                                                                                  │
│    - `specs/003-product-consumer-ordercancelled/plan.md`                                                                                        │
│    - `specs/003-product-consumer-ordercancelled/quickstart.md`                                                                                  │
│    - `specs/003-product-consumer-ordercancelled/research.md`                                                                                    │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
✦
我已閱讀所有設計文件，現在將根據計畫產生 tasks.md 檔案。
╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ✓  WriteFile Writing to specs\\tasks.md                                                                                                         │
│                                                                                                                                                 │
│     1 # Tasks: Product Stock Restoration on Order Cancellation                                                                                  │
│     2                                                                                                                                           │
│     3 **Input**: Design documents from `/specs/003-product-consumer-ordercancelled/`                                                            │
│     4                                                                                                                                           │
│     5 ## Format: `[ID] [P?] Description`                                                                                                        │
│     6 - **[P]**: Can run in parallel (different files, no dependencies)                                                                         │
│     7 - Include exact file paths in descriptions                                                                                                │
│     8                                                                                                                                           │
│     9 ## Phase 3.1: Setup & Contracts                                                                                                           │
│    10 - [ ] T001 [P] Create the DTO file `src/BC-Contracts/Lab.MessageSchemas.Orders/DataTransferObjects/OrderDetailsResponse.cs` based on the  │
│       definition in `specs/003-product-consumer-ordercancelled/contracts/OrderDetailsResponse.cs`.                                              │
│    11 - [ ] T002 [P] In the `SaleOrders.Applications` project, create a new query record `public record GetOrderDetailsQuery(Guid OrderId);`    │
│       in a new file `src/Order/DomainCore/SaleOrders.Applications/Queries/GetOrderDetails.cs`.                                                  │
│    12 - [ ] T003 [P] In the `SaleProducts.Domains` project, add a new public method `public void Restock(int quantity)` to the `Product`        │
│       entity in `src/Product/DomainCore/SaleProducts.Domains/Product.cs`.                                                                       │
│    13 - [ ] T004 [P] In the `SaleProducts.Applications` project, create a new command record `public record RestockProductCommand(Guid          │
 │       ProductId, int Quantity);` in a new file `src/Product/DomainCore/SaleProducts.Applications/Commands/RestockProduct.cs`.                   │
│    14                                                                                                                                           │
│    15 ## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3                                                                              │
│    16 **CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**                                                         │
│    17 - [ ] T005 [P] Create a new test class `GetOrderDetailsEndpointTests` in `tests/SaleOrders.Tests/GetOrderDetailsEndpointTests.cs`. It     │
│       should test that a `GET` request to `/api/orders/{orderId}` returns the correct order details. This test will fail until the endpoint is  │
│       implemented.                                                                                                                              │
│    18 - [ ] T006 [P] Create a new integration test class `OrderCancellationStockRestorationTests` in                                            │
│       `tests/SaleProducts.Tests/OrderCancellationStockRestorationTests.cs`. This test should follow the end-to-end scenario described in        │
│       `quickstart.md`. This test will fail.                                                                                                     │
│    19 - [ ] T007 [P] In `tests/SaleProducts.Domains.Tests/ProductTests.cs`, add a new unit test to verify that the `Restock` method correctly   │
│       increases the product's stock quantity.                                                                                                   │
│    20                                                                                                                                           │
│    21 ## Phase 3.3: Core Implementation (Order Context)                                                                                         │
│    22 - [ ] T008 Implement the `GetOrderDetailsQueryHandler` class in                                                                           │
│       `src/Order/DomainCore/SaleOrders.Applications/Queries/GetOrderDetails.cs`. This handler should fetch the order and its line items from    │
│       the database and return an `OrderDetailsResponse`.                                                                                        │
│    23 - [ ] T009 In `src/Order/Presentation/SaleOrders.WebApi/Controllers/OrdersController.cs`, implement a new public `GET` endpoint           │
│       `[HttpGet("{orderId}")]` that takes a `Guid orderId`, sends the `GetOrderDetailsQuery`, and returns the result.                           │
│    24                                                                                                                                           │
│    25 ## Phase 3.4: Core Implementation (Product Context)                                                                                       │
│    26 - [ ] T010 Create the `IOrderApiClient` interface and its implementation `OrderApiClient` in a new file                                   │
│       `src/Product/DomainCore/SaleProducts.Infrastructure/Clients/OrderApiClient.cs`. This client will have one method                          │
│       `Task<OrderDetailsResponse> GetOrderDetailsAsync(Guid orderId);` that calls the endpoint created in T009.                                 │
│    27 - [ ] T011 Implement the `RestockProductCommandHandler` class in                                                                          │
│       `src/Product/DomainCore/SaleProducts.Applications/Commands/RestockProduct.cs`. This handler should load the `Product` aggregate, call     │
│       the `Restock` method, and save the changes.                                                                                               │
│    28 - [ ] T012 Implement the `OrderCancelledHandler` class in                                                                                 │
│       `src/Product/Presentation/SaleProducts.Consumer/IntegrationEventHandlers/OrderCancelledHandler.cs`. This class will handle the            │
│       `OrderCancelled` event. It must use the `IOrderApiClient` to get order details and then dispatch a `RestockProductCommand` for each line  │
│       item in the response. Implement idempotency checks to avoid processing the same event twice.                                              │
│    29                                                                                                                                           │
│    30 ## Phase 3.5: Polish & Verification                                                                                                       │
│    31 - [ ] T013 [P] Register the `IOrderApiClient` and its implementation for dependency injection in the `SaleProducts.Infrastructure`        │
│       project's service extension method.                                                                                                       │
│    32 - [ ] T014 [P] Add DI registration for the `GetOrderDetailsQueryHandler` in the `SaleOrders.Applications` project's service extension     │
│       method.                                                                                                                                   │
│    33 - [ ] T015 [P] Review all new public classes and methods and add XML comments in Traditional Chinese, as required by the project's        │
│       contribution guidelines.                                                                                                                  │
│    34 - [ ] T016 Run `dotnet test` from the root directory and ensure all tests, including the new ones, pass.                                  │
│    35 - [ ] T017 Manually verify the entire workflow by following the steps outlined in                                                         │
│       `specs/003-product-consumer-ordercancelled/quickstart.md`.                                                                                │
│    36                                                                                                                                           │
│    37 ## Dependencies                                                                                                                           │
│    38 - `T001`-`T004` (Setup) must be done before other tasks.                                                                                  │
│    39 - `T005`-`T007` (Tests) must be done before `T008`-`T012` (Implementation).                                                               │
│    40 - `T009` depends on `T008`.                                                                                                               │
│    41 - `T012` depends on `T010` and `T011`.                                                                                                    │
│    42 - `T013`-`T017` (Polish) must be done after implementation is complete.                                                                   │
│    43                                                                                                                                           │
│    44 ## Parallel Example                                                                                                                       │
│    45 ```                                                                                                                                       │
 │    46 # The following setup and test tasks can be run in parallel:                                                                              │
 │    47 Task: "T001 [P] Create the DTO file src/BC-Contracts/Lab.MessageSchemas.Orders/DataTransferObjects/OrderDetailsResponse.cs"               │
 │    48 Task: "T002 [P] In the SaleOrders.Applications project, create a new query record..."                                                     │
 │    49 Task: "T005 [P] Create a new test class GetOrderDetailsEndpointTests..."                                                                  │
 │    50 Task: "T006 [P] Create a new integration test class OrderCancellationStockRestorationTests..."                                            │
 │    51 ```                                                                                                                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
✦ tasks.md 檔案已成功產生。


- 檔案路徑: C:\Github\YuChia\dotnet-mq-arch-lab\specs\003-product-consumer-ordercancelled\tasks.md
  現在已準備好開始執行實作任務。

```
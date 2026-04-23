# Problem Frame Authoring Guide

本指南說明如何從既有的 `requirement` / `spec` / 程式碼快速萃取出第一版 Problem Frame，並讓 `spec-compliance-validator` 有可用輸入。

## 定位

把 Problem Frame 視為這條鏈上的中間層：

`requirement -> spec -> problem frame -> BDD / SbE -> TDD -> implementation`

它不取代 DDD / CA，也不取代 requirement / spec。
它的用途是把單一 use case 壓縮成結構化、可驗證、可追溯的規格。

## 適用情境

優先用在這些情況：

- 高外部系統依賴
- 複雜錯誤處理或狀態轉換
- callback / message / reconciliation 存在
- 需要明確驗證 idempotency、timeout、authority boundary
- 要把 acceptance 與測試覆蓋做嚴格 trace

這類情況以 `CommandedBehaviorFrame (CBF)` 為優先。

## 不必先做的事

- 不必先完整學完 Problem Frames 學科
- 不必先重寫整份 requirement 或 spec
- 不必先為整個系統導入

先挑一個 use case 做第一版即可。

## 最小輸入來源

第一版 authoring 優先使用這些來源：

1. `.dev/requirement/` 的 business goal、限制、成功條件
2. `.dev/specs/` 的 use case flow、例外情境、欄位與 API 行為
3. ADR / architecture rules
4. 既有程式碼與測試
   當需求與規格不完整時，用來補出實際 state、event、error mapping

## 快速萃取流程

### Step 1. 選一個 use case，不要選一個 bounded context

正確粒度：

- `authorize-payment`
- `copy-lane`
- `ship-order`

錯誤粒度：

- `payments`
- `workflow`
- `order management`

Problem Frame 應該以單一行為單位建立，而不是整個模組。

### Step 2. 判斷先用 CBF 還是 SWF

若 use case 有 command、狀態改變、外部回應、事件、前後條件，先用 `CBF`。

若主要是 workpiece 操作、約束驗證、acceptance criteria 展開，且不強調 frame concerns，才考慮 `SWF`。

在目前 repo 的導入起點，建議先只做 `CBF`。

### Step 3. 先寫一張 extraction sheet

在開始填 YAML 前，先把來源文件壓成這些欄位：

- use case name
- actor / trigger
- input fields
- preconditions
- success outcome
- failure outcomes
- domain events
- external systems
- external authority facts
- timeout / retry / duplication rules
- audit fields / trace IDs
- acceptance scenarios

這一步若做對，後面的 YAML 只是重排，不是重新思考。

### Step 4. 從 requirement/spec 分流到各檔案

#### `frame.yaml`

放這些內容：

- `frame_type`
- use case summary
- `problem_world_facts`
- `frame_concerns`
- `commanded_behavior`

來源判斷：

- requirement 裡的 business boundary、外部依賴、不可控因素
- spec 裡的 external API / callback / MQ 說明

#### `machine/machine.yaml`

放這些內容：

- command processing steps
- error handling outcomes
- constraint enforcement

來源判斷：

- spec 的主流程 / 例外流程
- application service / handler 現況
- API timeout、retry、reconciliation 規則

#### `machine/use-case.yaml`

放這些內容：

- input fields
- preconditions
- postconditions
- output / failure outcomes

來源判斷：

- request DTO
- command / handler input
- spec 中明確的前置條件與完成條件

#### `controlled-domain/aggregate.yaml`

放這些內容：

- aggregate contracts
- invariants
- behavior signature
- domain events
- semantic tags

來源判斷：

- aggregate method
- domain event class
- domain state constraints
- code review checklist 中提到的 semantics

#### `acceptance.yaml`

放這些內容：

- Given / When / Then scenarios
- `traces_to`
- `tests_anchor`

來源判斷：

- acceptance criteria
- example flow
- 現有測試案例
- 業務最在意的正向 / 反向 / edge case

## 從程式碼逆向補第一版

如果 requirement / spec 不完整，可以從程式碼逆向補，但要標示這是「observed behavior」，不是純需求真相。

優先讀：

- command/query handler
- aggregate method
- domain events
- controller / adapter request model
- contract tests / use case tests

逆向時要特別補這三類常漏資訊：

- 哪些成功條件其實是外部系統決定
- 哪些錯誤只是暫時性失敗，不應被建模成 terminal failure
- 哪些 callback / retry 需要 idempotency

## 外部系統 use case 的最小問題分析

只要整合外部系統，至少補這五件事：

1. 哪個系統是 authority
2. 哪些結果可能延遲到達
3. 哪些請求或 callback 可能重複
4. timeout 發生時本系統允許宣稱到什麼程度
5. 哪些識別值必須保留給 support / audit / reconciliation

這五件事通常就是 `frame_concerns` 與 `problem_world_facts` 的核心。

## 第一版品質門檻

第一版不要追求學術完整，先達到這些門檻：

- 目錄與檔名符合 validator 預期
- input / preconditions / postconditions 明確
- 至少一個 aggregate behavior 與 domain events 對上
- acceptance scenarios 能 trace 到 requirement / spec
- `tests_anchor` 可以指向未來或既有測試名稱
- external constraints 沒被省略

## 推薦 authoring 節奏

1. 先填 `machine/use-case.yaml`
2. 再填 `aggregate.yaml`
3. 再補 `frame.yaml`
4. 最後用 `acceptance.yaml` 收斂 GWT 場景

原因：

- `use-case.yaml` 最接近現有 spec
- `aggregate.yaml` 最接近 DDD 模型
- `frame.yaml` 需要先想清楚外部世界事實
- `acceptance.yaml` 最適合最後整合

## Prompt 範本

### 從 requirement/spec 起草

```text
Use the repository's problem-frame authoring assets to draft a first CBF problem frame.

Inputs:
- requirement files: <paths>
- spec files: <paths>
- supporting code or tests: <paths or none>
- target use case: <name>

Tasks:
1. Extract the minimum authoring sheet from the inputs.
2. Decide whether CBF is appropriate and explain why.
3. Draft:
   - frame.yaml
   - machine/machine.yaml
   - machine/use-case.yaml
   - controlled-domain/aggregate.yaml
   - acceptance.yaml
4. Mark every inferred item as inferred if it is not directly stated in the sources.
5. List open questions that block 100% spec compliance validation.
```

### 從程式碼逆向起草

```text
Use the repository's problem-frame authoring assets to reverse-draft a first problem frame from code.

Inputs:
- handler files: <paths>
- aggregate files: <paths>
- event files: <paths>
- tests: <paths>

Tasks:
1. Reconstruct the likely use case contract and external constraints.
2. Draft a first CBF problem frame.
3. Separate direct evidence from inferred behavior.
4. Identify mismatches between observed code behavior and missing requirement/spec truth.
```

## 與其他 skill 的搭配

- `problem-frame-author`
  - 起草第一版 problem frame
- `bdd-gwt-test-designer`
  - 把 `acceptance.yaml` 轉成 Given-When-Then 測試設計
- `spec-compliance-validator`
  - 實作與測試完成後做 100% gate

## 建議的最小採用策略

不要一次把整個專案都 problem-frame 化。

建議順序：

1. 選 1 個高外部依賴 use case
2. 建第一版 problem frame
3. 用它導出 BDD 場景
4. 完成實作與測試
5. 再用 validator 驗證
6. 評估成本與收益後，再決定是否擴大

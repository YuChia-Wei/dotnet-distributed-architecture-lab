# BDD GWT Test Designer Skill Guide

本文件說明如何從使用者角度呼叫 `bdd-gwt-test-designer` skill。

## Design 與 Review

要求新增或修訂情境時使用 `design`；要求檢查既有情境時使用 `review`。
Review 固定輸入版本，回傳 AC 覆蓋、Then 可觀察性、前置條件、邊界／失敗案例
與測試層級的 findings、依據、影響及不確定性，保留原 artifact。修訂是另一個
已授權的 design 動作。作者自檢須標示 self-check；使用相同 skill 的其他 reviewer
仍需證明作者關係與受審版本，才能主張獨立審查。這些結果不代表 spec compliance。

例如：「用 `bdd-gwt-test-designer` review 這份固定版本 scenario notes，逐項對照
AC，說明缺漏、有效替代方案與待釐清資訊，不修改原文、不實作測試。」

## 這個 Skill 可以做什麼

適合用在下列工作：

- 從 requirement / spec / acceptance criteria 拆出 Given-When-Then scenarios
- 為 use case、aggregate、reactor、controller 設計測試情境
- 規劃 assertion points、負向案例、邊界案例
- 在寫測試前先整理 BDD/Gherkin 形式的測試設計
- 當輸入直接提供 `.feature`、使用者明確要求設計/產出，或 target profile 採用 runner 時，設計可落成 `.feature` 的內容

## 測試風格底線

- 本 skill 的情境設計採 Given-When-Then，不以 Arrange-Act-Assert（3A）取代。
- 實作工具依 target 選擇。採用 .NET profile 時，依其規則使用 xUnit／BDDfy 預設及明確 opt-out；不把這些工具要求套用到其他 target。
- `.feature` 是選配。未直接提供、未被明確要求且 target profile 未採用 runner 時，不主動建立 `.feature` 或相關配套。

## 這個 Skill 不應該做什麼

不應該拿來做：

- 直接實作 xUnit 測試程式碼
- 修改 production code
- 代替 architect 決定架構邊界
- 代替 reviewer 判定程式碼缺陷

## 它和其他 Skill / Workflow 的關係

- `bdd-gwt-test-designer`:
  - 先做測試情境設計
- `slice-implementer` 與其適用 test prompts / subagents:
  - 在具備實作授權後，依 target 選定工具承接情境；本 skill 不建立 `role_execution`，也不宣稱已執行測試
- `code-reviewer`:
  - 檢查測試是否符合規範、是否缺 coverage
- `ddd-ca-hex-architect`:
  - 若規格本身有邊界或語意不清，先覆核架構方向

若 repo 已採用 test spec workflow：

- scenario 設計結果應優先沉澱到 `.dev/specs/tests/`
- production behavior truth 仍應留在 `.dev/specs/domains/`
- test spec 路徑應依測試目標選擇：
  - aggregate -> `aggregate/`
  - use case -> `use-cases/`
  - repository/MQ/gateway -> `integration/`
  - cross-BC flow -> `cross-domain/`
  - full journey -> `e2e/`

## 典型適用情境

- 你有 spec，但還不想直接生成測試碼
- 你想先確認 acceptance criteria 是否完整可測
- 你要把既有需求整理成 GWT scenarios 給其他 agent 接手
- 你要補測試，但先想知道應該有哪些情境

## 從情境穩定交接到 GWT 方法

設計輸出保留 scenario ID、來源／AC、具體 Given 資料、主要 When 與每個 Then
的預期值。實作後由接收者補上測試檔、方法、step 與斷言位置，依
[GWT 交接契約](../../../.ai/assets/shared/GWT-TEST-HANDOFF-CONTRACT.md) 逐項核對。
參數化測試可以共用方法，但每筆資料仍要有可辨識的 ID 與結果。

測試本文應讀得出行為：`GivenMonthlyBudget(...)` 建立資料，
`WhenQueryingBudget(...)` 執行真實待測物件，`ThenAmountShouldBe(...)` 驗證結果。
重要數值留在本文或 theory 資料列，mock 與建構細節放入 helper。
Then 不重跑待測操作、不抄演算法重算預期值；只寫 GWT 註解或名稱還不夠。

採用 .NET profile 時可參考
[可執行範例](../../../.ai/assets/tech-stacks/dotnet-backend/examples/bdd-step-methods/README.md)：
BDDfy 預設與明確 opt-out 的 plain xUnit 使用相同情境與預期結果。具體實作仍交給
`slice-implementer` 及適用的 test role；已有實作授權就一起交接，毋須再確認一次。
review 檢查 scenario 與實際斷言的對應，test command 提供執行結果；兩者都要保留。

```text
Use slice-implementer in generic test-only mode to implement these approved GWT scenarios.
Preserve scenario/data-row IDs and every observable Then outcome.
Follow the target's selected test framework and BDDfy/default or explicit opt-out.
Express each test body with behavior-named Given/When/Then methods.
Return the scenario-to-test/step/assertion mapping and actual execution evidence;
mark any missing or unexecuted case explicitly.
```

## 怎麼下 Prompt

好的 prompt 至少應包含：

1. 來源文件或需求描述
2. 目標測試層級
3. 是否只要設計，不要實作
4. 是否要包含負向案例與邊界案例

## 範本 1：從 spec 設計 scenarios

```text
Use $bdd-gwt-test-designer to design Given-When-Then test scenarios from this spec.

Context:
- Source: [target-repository production spec path]
- Target level: use case test
- Do not implement test code yet

Focus on:
- map acceptance criteria to scenarios
- include negative and edge cases
- identify assertion points

Return:
1. inputs used
2. scenario set in Given-When-Then form
3. recommended test level
4. assertion notes
5. recommended test spec path under `.dev/specs/tests/`
6. ambiguities or missing rules
```

建議路徑範例：

- `.dev/specs/tests/<context>/use-cases/<use-case>.test-spec.md`
- `.dev/specs/tests/<context>/integration/<integration-target>.test-spec.md`
- `.dev/specs/tests/cross-domain/<scenario>.test-spec.md`

## 範本 2：從既有程式行為逆向整理 scenarios

```text
Use $bdd-gwt-test-designer to reverse-engineer Given-When-Then scenarios from the current implementation.

Context:
- Target code: [files/modules]
- Goal: understand what should be tested before rewriting tests
- Do not change code

Focus on:
- current observable behaviors
- missing scenario coverage
- negative paths

Return:
1. behaviors discovered
2. scenario set
3. assertion notes
4. risks or ambiguities
```

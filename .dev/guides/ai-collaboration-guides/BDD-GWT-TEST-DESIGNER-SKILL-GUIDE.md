# BDD GWT Test Designer Skill Guide

本文件說明如何從使用者角度呼叫 `bdd-gwt-test-designer` skill。

## 這個 Skill 可以做什麼

適合用在下列工作：

- 從 requirement / spec / acceptance criteria 拆出 Given-When-Then scenarios
- 為 use case、aggregate、reactor、controller 設計測試情境
- 規劃 assertion points、負向案例、邊界案例
- 在寫測試前先整理 BDD/Gherkin 形式的測試設計

## 這個 Skill 不應該做什麼

不應該拿來做：

- 直接實作 xUnit 測試程式碼
- 修改 production code
- 代替 architect 決定架構邊界
- 代替 reviewer 判定程式碼缺陷

## 它和其他 Skill / Workflow 的關係

- `bdd-gwt-test-designer`:
  - 先做測試情境設計
- 現有 test generation prompts / subagents:
  - 把設計轉成 xUnit + BDDfy 測試
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
- Source: [.dev/specs/domains/...]
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

- `.dev/specs/tests/order/use-cases/place-order.test-spec.md`
- `.dev/specs/tests/inventory-item/integration/decrease-stock-repository.test-spec.md`
- `.dev/specs/tests/cross-domain/place-order-and-reserve-stock.test-spec.md`

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

# BDD GWT Test Designer Pair Guide

本文件說明 `bdd-gwt-test-designer` 應如何和 repo 內既有的 test generation、review、architecture workflow 搭配使用。

## 核心定位

- `bdd-gwt-test-designer`
  - 先做 Given-When-Then 測試設計
  - 拆 scenarios、assertion points、coverage gaps
- 既有 test generation sub-agents
  - 把 scenario 設計轉成 xUnit + BDDfy 測試碼
- `code-reviewer`
  - 檢查測試是否符合規範、coverage 是否足夠
- `ddd-ca-hex-architect`
  - 當需求或 spec 本身有邊界語意問題時先覆核

## 建議搭配順序

### 1. 先設計 GWT scenarios

使用 `bdd-gwt-test-designer`：

- 從 requirement / spec / AC 拆出 scenarios
- 判定 test level
- 規劃 Then assertions 與資料準備
- 若要保存測試意圖，將結果整理到 `.dev/specs/tests/`
- 路徑依測試目標選擇 `aggregate/`、`use-cases/`、`integration/`、`cross-domain/`、`e2e/`

### 2. 再生成測試程式碼

依測試類型交給 delegated sub-agent workflow：

- use case test:
  - `.ai/assets/sub-agent-role-prompts/usecase-test-sub-agent/sub-agent.yaml`
- aggregate test:
  - `.ai/assets/sub-agent-role-prompts/aggregate-test-sub-agent/sub-agent.yaml`
- reactor test:
  - `.ai/assets/sub-agent-role-prompts/reactor-test-sub-agent/sub-agent.yaml`
- controller test:
  - `.ai/assets/sub-agent-role-prompts/controller-test-sub-agent/sub-agent.yaml`

### 3. 最後做 review

使用 `code-reviewer`：

- 檢查 Given / When / Then 是否落實
- 檢查 assertions 是否完整
- 檢查是否符合 xUnit + BDDfy + no BaseTestClass 規則

## 何時要先交給 Architect

下列情況先交給 `ddd-ca-hex-architect`：

- spec 本身邊界不清
- acceptance criteria 混了多個 use case
- 不知道 scenario 應該落在哪個 test level
- domain language / API / event 命名本身有語意衝突

architect 覆核後，再回到 `bdd-gwt-test-designer` 繼續拆 scenario。

## 典型工作流

```text
1. requirement / spec
2. bdd-gwt-test-designer
3. `.dev/specs/tests/` test spec
4. test generation sub-agent
5. code-reviewer
6. 必要時回到 bdd-gwt-test-designer 補 scenario gaps
```

## 不建議的用法

- 不要跳過 scenario design 就直接大批生成測試
- 不要讓 `bdd-gwt-test-designer` 直接充當 test code generator
- 不要讓 test generation workflow 自行發明缺失的 acceptance criteria
- 不要把 architecture ambiguity 當成測試設計問題硬解

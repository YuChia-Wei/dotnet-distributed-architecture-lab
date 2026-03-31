# Test Specs

本目錄放置 BDD / TDD / acceptance-oriented 的測試規格文件。

## 目的

- 保存「要驗證什麼」而不是「要怎麼實作」
- 為 BDD、TDD、Given-When-Then、scenario design 提供固定位置
- 避免把測試意圖混進 production-facing spec 或 workflow task

## 與 `.dev/specs/` 的分工

- `.dev/specs/domains/`
  - 描述 production behavior、aggregate、use case、adapter contract
- `.dev/specs/tests/`
  - 描述測試場景、驗證重點、前置條件、邊界條件、red-green-refactor 切分

簡單判斷：

- 如果文件回答「系統應該做什麼」 -> 放 `.dev/specs/domains/`
- 如果文件回答「我要如何驗證它真的做到」 -> 放 `.dev/specs/tests/`

## 建議結構

```text
.dev/specs/tests/
  README.MD
  TEST-SPEC-GUIDE.MD
  <domain>/
    aggregate/
      <aggregate-name>.test-spec.md
    app-services/
      <service-name>.test-spec.md
    domain-services/
      <service-name>.test-spec.md
    integration/
      <target-name>.test-spec.md
    use-cases/
      <use-case>.test-spec.md
  cross-domain/
    <flow-name>.test-spec.md
  e2e/
    <journey-name>.test-spec.md
```

## 目錄分類原則

- `aggregate/`
  - 驗證 aggregate invariant、state transition、domain events
- `app-services/`
  - 驗證 application service orchestration；若 repo 主要以 use case handler 為主，可暫時少用
- `domain-services/`
  - 驗證 domain service decision logic；只有真的存在獨立 domain service 時才使用
- `integration/`
  - 驗證 repository + database、MQ contract、consumer/producer、external gateway
- `use-cases/`
  - 驗證 command/query handling、input/output、協作邏輯
- `cross-domain/`
  - 驗證跨 bounded context 的流程，不歸屬單一 domain
- `e2e/`
  - 驗證完整旅程，例如 UI/API 到 MQ/DB 的端對端流程

## 分類決策順序

先問「主要要驗證哪一層」：

- 若焦點是 business invariant -> `aggregate/`
- 若焦點是 command/query flow -> `use-cases/`
- 若焦點是 database / MQ / external adapter -> `integration/`
- 若焦點跨多個 domain -> `cross-domain/`
- 若焦點是完整使用者旅程 -> `e2e/`

`app-services/` 與 `domain-services/` 是保留分類，不要求一開始就全部啟用。

## 適合放這裡的內容

- Given-When-Then scenarios
- acceptance criteria to assertion map
- red/green/refactor test slices
- edge cases and failure scenarios
- test-level recommendation（unit / integration / contract / end-to-end）

## 不適合放這裡的內容

- 實作程式碼
- repository 具體實作細節
- 僅供 agent 臨時使用的 scratch notes
- 取代 `.dev/specs/` 的 production behavior 規格

# .NET Validator Phase 2 需求

## Metadata

- Version: 0.1
- Date: 2026-07-04
- Owner: YuChia-Wei
- Status: Approved for implementation

## 目標

以 Roslyn analyzer 完整取代 controller compliance 的 grep-based C# 判斷，並讓 `check-all.sh` 不再執行 `check-controller-compliance.sh`。

## Functional Requirements

### FR-1：Controller 必須標示為 API Controller

- 非 abstract 且名稱以 `Controller` 結尾的 controller class 必須具有 `ApiControllerAttribute`。
- Diagnostic ID：`DBA1004`。

### FR-2：Controller 不得直接存取 Persistence

- Controller 不得引用 `DbContext` 型別。
- Controller 不得呼叫 `SaveChanges` 或 `SaveChangesAsync`。
- Diagnostic ID：`DBA1005`。

### FR-3：Controller 不得直接建構 Handler / UseCase

- Controller 不得使用 `new` 建立名稱以 `Handler` 或 `UseCase` 結尾的型別。
- 依賴必須透過 constructor injection 或 framework dispatch mechanism。
- Diagnostic ID：`DBA1006`。

### FR-4：移除文字分析 Script

完成 analyzer 與測試後：

- 移除 `.ai/scripts/check-controller-compliance.sh`。
- 移除 `.ai/scripts/generated/check-controller.sh`。
- `check-all.sh` 不得再呼叫 controller grep check。
- 更新 `.ai/scripts/README.md` 與 validator mapping。

## Constraints

- Analyzer 必須使用 syntax / semantic model，不以 source text regex 判斷。
- 不在本 phase 實作跨 assembly Presentation architecture tests。
- 不移除其他尚未完成 replacement 的 compliance scripts。

## Acceptance Criteria

- `DBA1004`、`DBA1005`、`DBA1006` 具有 positive 與 negative tests。
- Analyzer test suite 全部通過。
- Controller grep scripts 已移除。
- `check-all.sh` 只透過 analyzer test stage涵蓋 controller rules。
- Active docs 不再把 controller grep check 列為 transitional executable check。
- `git diff --check` 通過。

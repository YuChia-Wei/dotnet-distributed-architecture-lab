# .NET Validator Phase 3 需求

## Metadata

- Title: .NET Validator Phase 3
- Version: 0.1
- Date: 2026-07-05
- Owner: YuChia-Wei
- Status: Implemented
- In Scope: Mapper、Aggregate、UseCase、Projection 的 validator ownership、dotnet-native validation 與對應 script retirement
- Out of Scope: Repository interface 規範、dependency/version validation、產品專屬架構規則

## Context & Goals

Phase 2 已以 Roslyn Analyzer 取代 Controller grep validation，但 Mapper、Aggregate、UseCase 與 Projection 仍在 `check-all.sh` 中列為待替換項目。

Phase 3 的目標不是把 grep 規則逐字改寫成 C#，而是先依規則性質選擇可靠的 enforcement mechanism：

| 規則性質 | Owner |
| --- | --- |
| 格式、命名與 C# coding style | `.editorconfig`、standard .NET analyzers、formatter |
| 可由 syntax / semantic model 確定的架構規則 | Custom Roslyn Analyzer |
| 跨型別、組件或 EF Core model registration | Architecture test 或 configuration test |
| Business invariant、mapping completeness 與設計意圖 | Unit/integration test 與 AI review |

成功標準是每個被移除的 script 都有等價或更可靠的 replacement，且不把無法機械證明的軟體設計品質偽裝成 CI gate。

## Personas

- Framework Maintainer：維護可重用的 .NET backend validation template。
- Application Engineer：在目標 repository 中取得明確且低誤判的 diagnostics。
- AI Agent：依 analyzer evidence 與 software engineering context 執行實作或 review，不以文字搜尋結果取代設計判斷。

## Functional Requirements

### FR-1：Rule Ownership Classification

- 每一項舊 script 規則必須分類為 `.editorconfig`、Roslyn Analyzer、architecture/configuration test、AI review 或移除。
- 已可由 standard .NET analyzer 支援的 coding style 不得重複實作 custom analyzer。
- `.editorconfig` 規則只有在 build、`dotnet format --verify-no-changes` 或其他 CI command 實際執行且 severity 足以阻擋時，才能宣稱為 gate。

現有與 Phase 3 diagnostics 的 ownership audit：

| Rule family | Existing `.editorconfig` coverage | Decision |
| --- | --- | --- |
| Field readonly、accessibility、naming、formatting、primary-constructor preference | Yes | 使用 standard IDE/.NET diagnostics，不建立 DBA rule |
| Repository query semantics | No | `DBA1001` 保留；Repository policy 另案整理 |
| UseCase dependency resolution 與 CQRS role mixing | No | `DBA1002`、`DBA1010`-`DBA1012` |
| Domain/aggregate infrastructure dependency | No | `DBA1003` |
| Event-sourced aggregate transition boundary | No | `DBA1009` |
| Controller API/persistence/application boundary | No | `DBA1004`-`DBA1006` |
| Static-only Mapper role與 forbidden architecture dependencies | No | `DBA1007`-`DBA1008` |
| Projection persistence writes | No | `DBA1013` |
| EF projection read-model registration | No | `DotnetBackendValidation` configuration test |

Custom analyzer 的存在只提供 semantic detection capability。各 target repository 必須能透過 `.editorconfig` 的 `dotnet_diagnostic.DBAxxxx.severity`，依 architecture profile 與團隊共識調整為 `none`、`suggestion`、`warning` 或 `error`。

### FR-2：Mapper Validation

Mapper 的角色是執行 Domain、Data 與 DTO 間的資料轉換，不應查詢 Repository、呼叫 UseCase/Handler，或承擔 business orchestration。

#### Static-only Mapper

- Mapper 必須是 `static class`，mapping methods 必須是 static。
- Mapper 必須是 deterministic pure transformation，不得持有 instance state、使用 DI、執行 I/O 或作出 business decision。
- Mapper 不得依賴 Repository、UseCase、Handler、clock、current-user context、network 或 database。
- Argument null handling 優先交由 standard analyzers、nullable reference types 或 tests，不以方法內是否出現固定文字判斷。
- 欄位是否完整對稱映射必須由 mapping tests 或 AI review 驗證，不由 syntax analyzer 猜測。

需要 instance dependency、外部資料或 orchestration 的轉換不屬於 Phase 3 定義的 Object Mapper。未來遇到這類需求時，依責任使用下列角色：

| 行為 | 建議角色 |
| --- | --- |
| 合併多個來源建立物件 | Assembler |
| 查詢外部資料補充欄位 | Enricher |
| 協定或語意邊界轉換 | Translator / Adapter |
| 包含 business decision | Domain Service / Application Service |
| persistence rehydration orchestration | Repository Adapter |

上述角色表僅作未來分類參考；Phase 3 不建立其 analyzer、skill 或 implementation template。

### FR-3：Aggregate Validation Profiles

Aggregate validation 採用 shared baseline 加上 type-specific profile：

#### Shared Baseline

- `AggregateRoot` 與 `EsAggregateRoot` 都不得依賴 `DbContext` 或其他 Infrastructure type。
- 兩者都必須維護 invariant、封裝狀態變更，並由 tests 與 AI review 驗證 business behavior。
- 一般 Aggregate 可以發布 Domain Event，但不因此成為 Event Sourcing Aggregate。

#### Event Sourcing Profile

- 只有繼承 `EsAggregateRoot` 的 Aggregate 強制使用 `Apply/When` event transition model。
- Event Sourcing Aggregate 必須支援 event replay，且不得繞過 event transition 直接建立不可重播的狀態。
- 可由 analyzer 判定的 type hierarchy 與 forbidden direct mutation 才能成為 diagnostic；event history completeness 由 tests 與 review 驗證。

#### Normal Aggregate Profile

- 繼承一般 `AggregateRoot` 的 Aggregate 不強制使用 `Apply/When`。
- Normal Aggregate 可以直接在 domain method 中變更封裝狀態，並視需求發布 notification-style Domain Events。
- 不得因為沒有 event history 或 replay constructor 而產生 Event Sourcing diagnostic。

兩種 Aggregate 若完全採用相同規範，雖可降低文件與工具分支、提高表面一致性，也較容易將 normal Aggregate 遷移至 Event Sourcing；但會迫使不需要 replay 的模型承擔 event schema、versioning、rehydration 與測試成本，並混淆「Domain Event」和「Event Sourcing source of truth」。因此 Phase 3 採 shared baseline 加 profile-specific rules，不採完全相同規範。

### FR-4：UseCase Validation

- 保留 `DBA1002` 對 `IServiceProvider` constructor injection 的禁止。
- 補足可可靠判定的 Service Locator 或 property injection 規則。
- Command 與 Query 分離只能依明確的 marker interfaces／base types 判定，不以 `Handle(`、檔名或 method name 作為 CI gate。
- `private readonly`、公開 constructor、primary constructor 等 coding style 由 `.editorconfig` 與 standard analyzers 管理，不建立 custom architecture diagnostic。

### FR-5：Projection Configuration Validation

- 以 `IProjectionReadModel` marker interface 識別需要 EF Core model registration 的 projection read model。
- EF Core configuration test 必須列舉 `IProjectionReadModel` implementations，並確認每一型別存在於 `DbContext.Model`。
- Dapper-only projection/query DTO 不必實作 `IProjectionReadModel`，也不受 EF Core registration gate 約束。
- Query service interface（例如 `IRecordProjection`）不得因名稱包含 `Projection` 而被視為 EF Core entity。
- 不再以檔名、`DbSet<` source text 或 `Entity<` source text 判定 registration。

### FR-6：Transitional Script Retirement

- Mapper、Aggregate、UseCase、Projection 的 script 只能在其可機械驗證規則已有 replacement 且測試通過後移除。
- 不適合自動化的規則必須明確轉移至 AI review 或 test guidance，不得因 script 移除而消失。
- `check-all.sh` 必須以 analyzer tests 或 configuration tests 取代完成項目的 TODO。
- Repository TODO 保留到獨立規範整理完成。

## Non-Functional Requirements

- Analyzer 必須使用 Roslyn syntax / semantic APIs，不得改用 source text regex。
- Diagnostics 必須具有 positive、negative 與 false-positive regression tests。
- Validator template 不得依賴單一產品的 namespace、aggregate name、projection name 或 folder layout。
- Rule ownership 必須可由文件追溯到 source standard、test 或 AI review context。

## Constraints & Assumptions

- Repository interface 規範將在另一個 worktree 與 conversation 重新整理，Phase 3 不修改 `DBA1001` 或 repository script。
- `EsAggregateRoot` 與 `AggregateRoot` 是目前 dotnet-backend profile 的 canonical type distinction。
- Projection marker interface 名稱暫定為 `IProjectionReadModel`；若實際 framework 已存在等價介面，實作時應採用既有 canonical type。
- 現有 `.editorconfig` 已包含 primary constructor 與多項 coding-style preference，但部分 severity 為 `suggestion` 或 `silent`，目前不等同 CI failure。
- Mapper 採 static-only policy；需要 instance dependency 或 orchestration 的轉換必須重新分類責任。

## Domain / Architecture Rules

- Custom analyzer 補足的是 standard tooling 無法表達的 architecture semantics，不是重複實作 formatter。
- Normal Aggregate 與 Event Sourcing Aggregate 共享 domain purity 與 invariant responsibility，但 persistence source of truth 不同。
- Projection registration 是 assembled EF Core model 的事實，應在 model 建立後驗證。
- AI review 保留對 design intent、business completeness 與合理 tradeoff 的判斷責任。

## Acceptance Criteria

- 每項 Phase 3 規則都具有明確 enforcement owner。
- Repository validation 沒有被 Phase 3 修改或移除。
- Mapper diagnostic 強制 static-only pure transformation policy。
- Event Sourcing diagnostics 只套用於 `EsAggregateRoot`。
- Normal `AggregateRoot` 不因缺少 `Apply/When` 被回報。
- UseCase custom diagnostics 不重複 `.editorconfig` 可處理的 coding style。
- EF Core projection registration 透過 `IProjectionReadModel` 與 model/configuration test 驗證。
- 每個被移除的 script 都有 replacement evidence 與通過的 tests。
- Analyzer 與 configuration-test suites 全部通過。
- `check-all.sh` 不再列出已完成的 Mapper、Aggregate、UseCase、Projection TODO。
- `git diff --check` 通過。

## Resolved Decisions

- Mapper 採 Option A：static-only。
- Option B 與其可能情境不納入 Phase 3。
- 超出 pure object mapping 的需求依角色參考表重新分類。

## References

- `.editorconfig`
- `.dev/requirement/DOTNET-VALIDATOR-PHASE-2-REQUIREMENTS.MD`
- `.dev/standards/coding-standards/mapper-standards.md`
- `.dev/standards/coding-standards/aggregate-standards.md`
- `.dev/standards/coding-standards/usecase-standards.md`
- `.dev/standards/coding-standards/projection-standards.md`
- `.ai/assets/tech-stacks/dotnet-backend/references/CODE-REVIEW-INDEX.MD`
- `.ai/scripts/check-all.sh`
- `tools/DotnetBackendAnalyzers/`

## Implementation Outcome

- Added `DBA1007`-`DBA1013` for Mapper, Event Sourcing Aggregate, UseCase, and Projection semantic rules.
- Extended `DBA1002` to cover primary constructors and non-constructor `IServiceProvider` dependencies.
- Added `DotnetBackendValidation` for marker-based EF Core projection model registration.
- Added a target-repository `.editorconfig` severity template covering `DBA1001`-`DBA1013`.
- Removed Mapper, Aggregate, UseCase, and Projection grep/config scripts after replacement validation passed.
- Retained Repository and dependency/version validation as explicit deferred work.


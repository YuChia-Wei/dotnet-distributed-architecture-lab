# ADR Consolidation Closure

## Outcome

本輪 ADR consolidation 已完成以下工作：

1. 建立 ADR first-pass consolidation report
2. 補上 workflow trigger conditions 的正式規則
3. 為 ADR index 建立狀態模型與 canonical source 欄位
4. 將 `ADR-031`、`ADR-041` 對應規則補成正式標準文件
5. 將多份已過時或已被取代的 ADR 內部狀態改為 historical / superseded
6. 建立 portable `standards/rationale/`，抽出可攜式模式選擇理由
7. 退役並移除已被標準與 rationale 完整承接的 ADR

## New Canonical Standards Added

- `.dev/standards/coding-standards/reactor-standards.md`

## Canonical Standards Expanded

- `.dev/standards/coding-standards/mapper-standards.md`

## Portable Rationale Added

- `.dev/standards/rationale/rest-api-resource-path-rationale.MD`
- `.dev/standards/rationale/generic-repository-only-rationale.MD`
- `.dev/standards/rationale/query-side-layering-rationale.MD`
- `.dev/standards/rationale/profile-based-testing-rationale.MD`
- `.dev/standards/rationale/skill-sub-agent-boundary-rationale.MD`

## Active ADRs Intentionally Kept

以下 ADR 目前仍保留為 `Active ADR`，因為尚未被其他 canonical 文件完整吸收：

- `ADR-002-orm-config-location`
- `ADR-005-ai-task-execution-standard-operating-procedure`
- `ADR-012-task-moved-event-design`
- `ADR-018-pbi-state-transition-invariant-handling`
- `ADR-024-test-isolation-and-domain-event-mapper`
- `ADR-049-dockerfile-explicit-csproj-copy-for-restore-cache`

## Historical / Superseded ADRs Normalized

本輪已將下列 ADR 的檔案內部狀態對齊為 historical / superseded：

- `ADR-004`
- `ADR-007`
- `ADR-013`
- `ADR-027`
- `ADR-028`
- `ADR-034`
- `ADR-036`
- `ADR-042`

## ADRs Retired After Rationale Extraction

以下 ADR 已被刪除，因為其規則與可攜式決策理由都已由 standards / rationale 承接：

- `ADR-006`
- `ADR-029`
- `ADR-046`
- `ADR-051`

## Practical Effect

- 使用者現在可以直接從 `INDEX.md` 看出哪些 ADR 還是 active source of truth
- 已落地的規則不需要再把 ADR 當成主要入口
- historical ADR 不再與 active guidance 混淆
- 可攜式決策理由已不再綁死在 project-specific ADR 中

## Suggested Next Slice

若要再進一步收斂 `.dev/adr/`，建議下一條 workflow 處理：

1. `ADR-002` 是否應落地到正式 ORM / persistence standard
2. `ADR-024` 是否應落地到 testing standard 或 framework integration guide
3. `ADR-049` 是否應落地到 deployment / docker guide
4. `ADR-012`、`ADR-018` 是否應移出 ADR，改為 domain-specific spec / historical note

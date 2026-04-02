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
8. 將 `ADR-050` 抽成可攜式 AI taxonomy guide
9. 將剩餘 active ADR 補成正式落點或降為 project-specific history
10. 退役已無 portable 價值的 Scrum / PBI project-specific ADR
11. 退役已完成知識抽取的舊 AI / workflow historical ADR

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

## New Portable Guides Added

- `.dev/guides/ai-collaboration-guides/SKILL-AND-SUB-AGENT-TAXONOMY-GUIDE.md`
- `.dev/guides/implementation-guides/PERSISTENCE-CONFIGURATION-GUIDE.md`
- `.dev/guides/implementation-guides/DOCKER-RESTORE-CACHE-GUIDE.md`

## Active ADRs Intentionally Kept

本輪結束後，`INDEX.md` 已無剩餘 `Active ADR`。
原先仍 active 的 ADR 已分別：

- 補成正式 canonical source
- 或降為 historical / project-specific history

## Historical / Superseded ADRs Normalized

本輪曾將下列 ADR 的檔案內部狀態對齊為 historical / superseded，作為後續退役前的過渡狀態：

- `ADR-004`
- `ADR-007`
- `ADR-013`
- `ADR-034`
- `ADR-036`
- `ADR-042`

## Historical / Superseded ADRs Retired

以下 ADR 已被刪除，因為它們只剩舊 AI / workflow / tooling history，active guidance 已由 canonical guide、workflow contract 或 sub-agent system 承接：

- `ADR-004`
- `ADR-007`
- `ADR-013`
- `ADR-034`
- `ADR-036`
- `ADR-042`
- `ADR-050`

## ADRs Retired After Rationale Extraction

以下 ADR 已被刪除，因為其規則與可攜式決策理由都已由 standards / rationale 承接：

- `ADR-006`
- `ADR-029`
- `ADR-046`
- `ADR-051`

## Historical / Project-Specific ADRs Retired

以下 ADR 已被刪除，因為它們只剩舊 Scrum / PBI feature history，沒有 portable rationale，也不再作為知識庫入口：

- `ADR-012`
- `ADR-018`
- `ADR-027`
- `ADR-028`

## Additional ADRs Reclassified After Backfill

- `ADR-002` -> `Landed in Standards`
- `ADR-005` -> `Landed in Standards`
- `ADR-024` -> `Landed in Standards`
- `ADR-049` -> `Landed in Standards`

## Practical Effect

- 使用者現在可以直接從 `INDEX.md` 看出哪些 ADR 只是歷史、哪些已被正式文件承接
- 已落地的規則不需要再把 ADR 當成主要入口
- historical ADR 不再與 active guidance 混淆
- 可攜式決策理由已不再綁死在 project-specific ADR 中
- 舊 Scrum / PBI feature history 已退出 portable ADR set，不會跟著知識庫複製到新專案
- 舊 AI / workflow / tooling ADR 也已退出 portable ADR set，日常入口改由 canonical guide 與 rationale 承接
- AI taxonomy、persistence configuration、docker restore cache 等知識已可跟著 portable knowledge base 一起帶走

## Suggested Next Slice

若要再進一步收斂 `.dev/adr/`，建議下一條 workflow 處理：

1. 是否要替 `ADR-003`、`ADR-019`、`ADR-020` 這些 landed ADR 補更多 portable rationale

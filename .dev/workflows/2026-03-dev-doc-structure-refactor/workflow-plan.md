# Dev Doc Structure Refactor Plan

## Metadata

- `plan_id`: `2026-03-dev-doc-structure-refactor`
- `owner_skill`: `ddd-ca-hex-architect`
- `status`: `completed`

## Context

- Problem statement:
  - `.dev/guides/` 與 `.dev/standards/` 目前混放 learning guides、design guides、implementation guides、troubleshooting guides、reference docs、true standards。
  - `.dev/guides/ai-collaboration-guides/` 已經從單純 skill guide 擴張成 collaboration workflows、contracts、strategies、prompt guides。
- Current scope:
  - 完成第一輪文件資訊架構重整：
    - 將 `.dev/ai-skill-guides/` 更名並收納到 `.dev/guides/ai-collaboration-guides/`
    - 將 `.dev/guides/` 拆成 `design-guides/`、`implementation-guides/`、`learning-guides/`
    - 將 `standards/` 中不屬於標準的文件移出
- Why refactor now:
  - 目前文件分類已開始影響人類與 AI agent 的理解效率。
  - 後續若直接繼續新增文件，重複定義與目錄語意漂移會更嚴重。

## Target Direction

- Target architecture summary:
  - 重新收斂 `.dev/standards/` 為規範、檢查表、單一真相。
  - 先將 `.dev/ai-skill-guides/` 更名並收納到 `.dev/guides/ai-collaboration-guides/`。
  - 再將 `.dev/guides/` 重整為更清楚的子分類，例如 learning / design / implementation。
  - 將本次整理視為文件結構重構，使用 `.dev/workflows/` 保存決策與任務進度。
- Key constraints:
  - 先建立 proposal 與 migration mapping，再決定是否搬移檔案。
  - 避免一次性大搬遷造成 link breakage 與索引失效。
- Non-goals:
  - 這一輪不重寫所有歷史文件內容。
  - 這一輪不直接變更每份文件的技術內容。

## Stages

### Stage 1
- Goal:
  - 建立目錄重整提案與 migration mapping。
- Scope:
  - 分析 `.dev/guides/`、`.dev/standards/`、`.dev/guides/ai-collaboration-guides/` 現況。
  - 產出 target structure proposal。
- Non-goals:
  - 不搬移檔案。
- Risks:
  - 分類定義若不夠清楚，後續仍可能反覆調整。
- Recommended implementer:
  - documentation refactor planning
- Status:
  - completed

### Stage 2
- Goal:
  - 依提案執行目錄搬遷與索引修正。
- Scope:
  - 搬移檔案、更新 README / INDEX / AGENTS 路徑。
- Non-goals:
  - 大幅改寫文件內容。
- Risks:
  - link breakage、讀者入口失效。
- Recommended implementer:
  - staged-refactor-implementer
- Status:
  - completed

## Validation Strategy

- Reviewer checkpoints:
  - 新舊目錄角色是否單一且清楚。
  - 搬遷對照表是否完整。
- Tests/validation expectations:
  - 至少檢查所有索引與關鍵文件引用路徑。

## Notes

- Open questions:
  - `standards` 與 `guides` 的界線是否要以文件用途還是讀者行為來界定
  - 是否還要為 `guides/` 與 `standards/` 補更細的 README / index 導覽


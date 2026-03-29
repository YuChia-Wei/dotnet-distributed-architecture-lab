# Portable AI Asset Architecture Refactor Plan

## Metadata

- `plan_id`: `2026-03-portable-ai-asset-architecture`
- `owner_skill`: `ddd-ca-hex-architect`
- `status`: `completed`

## Context

- Problem statement:
  - 目前 repo 同時使用 Codex、Gemini、GitHub Copilot 等多種 AI agents，但 AI 資產分成 `.ai/`、`.claude/skills/`、`.dev/guides/ai-collaboration-guides/` 三類後，仍缺少一套明確的「portable canonical source + agent wrapper」架構。
  - 使用者希望 skill、command prompts、workflow prompts 可攜且跨 agent 共用，但不希望將完整內容複製到 `.codex/`、`.claude/`、`.github/copilot/`、`.gemini/` 各自維護。
  - 目前 `.claude/skills/` 可視為 repo-local agent-specific skill definitions，但尚未定義中立 skill spec、command spec、adapter generation strategy。
- Current scope:
  - 為 portable AI assets 建立規劃、proposal、task checklist 與後續分階段重構策略。
  - 不在本階段直接搬動既有 skill 或 prompt 檔案。
- Why refactor now:
  - 若在沒有 canonical source 與 adapter strategy 的情況下繼續擴充 skill，之後導入更多 agent-specific runtime 將產生多份真相與更高維護成本。

## Target Direction

- Target architecture summary:
  - 將 AI 資產分成四層：
    1. Canonical source
    2. Human-facing guides
    3. Agent-specific wrappers
    4. Optional generation/sync tooling
  - Canonical source 優先放在中立且可版本控管的位置，不依附單一 agent runtime。
  - `.claude/skills/` 保留為現階段 agent-specific wrapper / runtime-facing definition。
  - `.ai/` 逐步收斂為跨 agent 可重用的 prompt、rule、script、spec source。
  - `.dev/guides/ai-collaboration-guides/` 保留為 human-facing guides 與策略說明。
- Key constraints:
  - 不應立即導入多份 agent-specific 目錄並手工同步。
  - 不應在 canonical source 尚未明確前就生成 `.codex/`、`.gemini/`、`.github/copilot/` wrappers。
  - 現有 `.claude/skills/` 不能在沒有替代入口的情況下被破壞。
- Non-goals:
  - 本輪不實作 `.codex/skills/` 安裝或同步機制。
  - 本輪不直接改寫所有既有 prompts 成新格式。
  - 本輪不承諾所有 agent 立即原生支援相同 skill runtime。

## Stages

### Stage 1
- Goal:
  - 完成現有 AI assets inventory 與 taxonomy。
- Scope:
  - 盤點 skill、command prompts、shared prompts、workflow guides、scripts。
  - 定義 asset types 與 canonical / wrapper / guide 的邊界。
- Non-goals:
  - 不搬檔案。
- Risks:
  - 若 taxonomy 不穩，後續 spec 與 generator 都會重做。
- Recommended implementer:
  - documentation planning
- Status:
  - completed

### Stage 2
- Goal:
  - 定義 canonical source schema 與目錄結構。
- Scope:
  - 決定 skill spec、command spec、prompt package 的最小欄位。
  - 決定 canonical 目錄位置與 naming rules。
- Non-goals:
  - 不產生 agent wrappers。
- Risks:
  - schema 太重會拖慢 adoption；太輕則無法生成 wrapper。
- Recommended implementer:
  - architecture planning
- Status:
  - completed

### Stage 3
- Goal:
  - 設計 agent wrapper strategy 與 generation/sync strategy。
- Scope:
  - 定義 `.claude/skills/` 如何從 canonical source 對應。
  - 評估 Codex / Gemini / Copilot 的 wrapper 最小需求。
  - 決定 generated vs thin-wrapper 模式。
- Non-goals:
  - 不全面生成所有 wrappers。
- Risks:
  - 若過早導入生成器，可能固化錯誤 schema。
- Recommended implementer:
  - architecture planning
- Status:
  - completed

### Stage 4
- Goal:
  - 選一個現有 skill 與一組 command prompts 作為 pilot migration。
- Scope:
  - 建立第一個 canonical skill spec。
  - 建立第一個 wrapper mapping。
  - 驗證 human guide、canonical source、agent wrapper 三層是否可共存。
- Non-goals:
  - 不一次遷移所有 AI assets。
- Risks:
  - pilot 選太複雜會拖慢整體策略驗證。
- Recommended implementer:
  - staged-refactor-implementer
- Status:
  - completed

### Stage 5
- Goal:
  - 完成 repo 內 portable AI asset architecture 的第一版落地。
- Scope:
  - 建立 canonical source 目錄。
  - 建立至少一組 skill wrapper strategy 與一組 command wrapper strategy。
  - 更新索引、guide、directory rules、agent routing 文件。
- Non-goals:
  - 不要求所有 agent runtime 在本階段都已可直接自動安裝。
- Risks:
  - 若範圍過大，可能需要將 rollout 切成多個 commit，但仍應在本 workflow 內收斂完成。
- Recommended implementer:
  - staged-refactor-implementer
- Status:
  - completed

### Stage 6
- Goal:
  - 補齊本機同步/安裝指南與後續擴充規則。
- Scope:
  - 提供 Codex 本機使用 canonical assets 的同步/安裝語法。
  - 定義 Claude / Codex / Gemini / GitHub Copilot 的 wrapper 路徑與維護原則。
  - 補 migration lesson learned 與後續新增規範。
- Non-goals:
  - 不保證每個 agent 都有同等完整的 runtime skill 能力。
- Risks:
  - 若把本機安裝與 repo portable 結構混在一起，會再次模糊 canonical source 與 runtime wrapper 的分工。
- Recommended implementer:
  - documentation finishing
- Status:
  - completed

## Validation Strategy

- Reviewer checkpoints:
  - Canonical source 是否明確且中立。
  - `.ai/`、`.claude/skills/`、`.dev/guides/ai-collaboration-guides/` 的分工是否單一。
  - 是否能避免四份 agent-specific 內容手工同步。
- Tests/validation expectations:
  - 至少完成一個 pilot skill 的 canonical-to-wrapper mapping。
  - 至少驗證一個 command prompt family 的 portable packaging。
  - 至少寫清楚四種 agent 的 repo-level wrapper 路徑與本機使用方式。

## Notes

- Open questions:
  - Canonical skill spec 是否應放在 `.ai/skills/`、`.ai/catalog/skills/` 或其他中立位置。
  - command prompts 是否應獨立成 `commands/`，還是保留在 `prompts/` 下以 metadata 補強。
  - 是否需要額外的 install/export script 才能讓 Codex/Gemini/Copilot 使用 wrapper。
- Dependencies:
  - 依賴目前已完成的 `.dev` / `.ai` / `.claude/skills/` 索引收斂結果。

## Follow-up Planning

### Codex Runtime Skill Gap

- Current state:
  - repo 內已定義 `.codex/skills/` root 與 `ddd-ca-hex-architect` pilot runtime wrapper。
  - 目前尚未定義完整的 canonical skill 批次同步/export 機制，也尚未驗證多個 skill 的擴大量產方式。
- Why this matters:
  - 使用者預期 `wrapper` 應能支援 Codex 直接調用 skill。
  - 若不明確區分 prompt wrappers 與 runtime skill wrappers，會持續混淆「repo portability」與「Codex installed skill」。
- Follow-up artifact:
  - `codex-runtime-skill-wrapper-plan.md`
  - `tasks/codex-runtime-skill-wrapper-planning.json`
- Planned next implementation scope:
  - 擴大 `.codex/skills/<skill-id>/SKILL.md` thin-wrapper model 到更多 skills
  - 定義 repo-local wrapper 與 `$CODEX_HOME/skills/` 的同步策略
  - 決定是手動維護 thin wrappers 還是由 canonical source 生成

### Command To Skill Convergence

- Current state:
  - `.codex/commands/` 已移除，且目前沒有活躍引用。
  - `.ai/assets/commands/` 已移除，原先的 command family 已收斂到 `.ai/assets/sub-agent-role-prompts/`。
  - `.ai/assets/` 中原本的 command-style / sub-agent-style prompts 已完成分類，僅保留 shared / explanatory / supporting materials。
  - canonical skill specs 已改用 `.ai/assets/skills/.../references/`，不再直接依賴 `.claude/skills/.../references/`。
- Why this matters:
  - skill-first 已成為目前 repo 的主要 runtime 模型。
  - 若 command-spec 與 command-style prompts 長期保留為平行入口，會再次造成模型混亂。
  - canonical skill spec 依賴 agent-specific references path，違反中立 canonical source 的方向。
- Follow-up artifact:
  - `stage-g-command-to-skill-convergence.md`
  - `command-to-skill-inventory.md`
  - `prompt-retention-checklist.md`
  - `tasks/stage-g-command-to-skill-convergence.json`
- Planned next implementation scope:
  - 清理仍殘留於 workflow 歷史文件中的舊 command-layer 描述
  - 保留必要的 explanatory / shared prompt materials，並維持其長期放置策略
  - 繼續收斂 handoff / stage notes / inventories，避免新的 session 誤讀過時模型
  - 更新 strategy docs 與 indexes 以反映最終的 skill + sub-agent-role 模型


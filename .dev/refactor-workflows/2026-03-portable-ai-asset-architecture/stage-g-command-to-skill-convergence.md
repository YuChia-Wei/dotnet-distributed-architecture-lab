# Stage G Command To Skill Convergence

本階段定義 repo 內 AI 協作資產的下一步重構方向：

- 移除 command 形式的 prompts / command-spec 作為主要入口
- 以 top-level skill + delegated sub-agent-role prompt 作為可執行型 AI 資產主軸
- 保留必要的說明型、規則型、shared prompt materials
- 將 canonical skill spec 對 `.claude/skills/.../references/` 的依賴搬到 `.ai/assets/skills/.../references/`

## Why This Stage Exists

本階段啟動時，portable AI asset architecture 已完成第一版落地，但仍有兩種舊模型殘留：

1. `.ai/assets/commands/` 仍保留 command-spec
2. `.ai/assets/` 中仍有多個以 `*-sub-agent-prompt.md` 或 task prompt 為中心的舊式入口

這與目前使用者已確認的方向不一致：

- Codex 已以 `.codex/skills/` 為唯一 runtime wrapper root
- 主流 AI agent tools 正逐步將 command / slash-prompt 模式收斂為 skill 或更結構化的 delegated assets
- canonical source 應避免持續依賴 agent-specific references 路徑

## Scope

- 盤點 `.ai/assets/commands/` 是否應退役，並確認其 canonical 承接位置
- 盤點 `.ai/assets/` 中哪些檔案屬於：
  - command-style prompts，應轉 skill 或退役
  - explanatory / rules / shared prompt materials，應保留
  - 需要使用者判斷的灰區資產
- 規劃 `.claude/skills/.../references/` 遷移到 `.ai/assets/skills/.../references/`
- 建立後續實作 checklist 與 task record

## Non-Goals

- 本階段不一次完成所有新 skill 的全文撰寫
- 本階段不新增 sync/export tooling
- 本階段不重新引入 `.codex/prompts/` 或 `.codex/commands/`

## Proposed Execution Order

1. 確認 `.codex/commands/` 移除後沒有活躍引用
2. 將 `.ai/assets/commands/` 視為待退役資產，盤點其對 `.ai/assets/` 的依賴
3. 對 `.ai/assets/` 建立保留 / sub-agent-role 化 / supporting-material / 退役分類
4. 先處理 canonical skill references 中立化
5. 依優先順序將 command-style prompts 收斂為正確的 canonical assets
6. 更新索引與 strategy docs

## Initial Decisions

- `.codex/commands/` 已由使用者手動移除，且目前未發現活躍引用
- `.codex/skills/` 暫不需要 sync/export tooling，只需保留簡單說明
- `.claude/skills/.../references/` 搬到 `.ai/assets/skills/.../references/` 應納入後續實作
- `*-sub-agent-prompt.md` 不應直接建模為 top-level skill，而應依角色收斂為 sub-agent-role prompt 或 supporting material

## Tooling Note

- 已確認 `apply_patch` 在目前執行環境下無法操作 `.codex*` 前綴路徑，會回傳 `windows sandbox: setup refresh failed`
- `.codex/skills/.../SKILL.md` 後續應改用 shell-based 精準編修
- `.ai/`、`.dev/`、`.claude/` 等其他路徑仍可正常使用 `apply_patch`

## Deliverables

- `command-to-skill-inventory.md`
- `prompt-retention-checklist.md`
- `tasks/stage-g-command-to-skill-convergence.json`

## Completion Criteria

- `.ai/assets/commands/` 已完成退役並自 repo 移除
- command-style prompts 已有正確的 migration target 或 retirement decision
- 保留型 prompts 有清楚分類與放置原則
- canonical skill specs 不再直接引用 `.claude/skills/.../references/`


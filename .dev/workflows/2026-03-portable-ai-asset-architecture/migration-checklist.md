# Portable AI Asset Migration Checklist

## Stage 1: Inventory And Taxonomy

- [ ] 列出現有 repo-local skills
- [ ] 列出現有 command prompts
- [ ] 列出 shared prompt fragments
- [ ] 列出 scripts / validators / generators
- [ ] 分類 human-facing guides vs agent-facing assets
- [ ] 標記哪些內容屬於 canonical source 候選
- [ ] 標記哪些內容屬於 agent wrapper

## Stage 2: Canonical Schema Design

- [ ] 定義 `skill.yaml` 最小欄位
- [ ] 定義 `command.yaml` 最小欄位
- [ ] 定義 prompt package 結構
- [ ] 定義 references / examples 放置規則
- [ ] 定義 naming rules
- [ ] 定義 human guide 與 canonical source 的對應規則

## Stage 3: Wrapper Strategy

- [ ] 定義 `.claude/skills/` 薄 wrapper 規則
- [ ] 定義未來 `.codex/` / `.gemini/` / `.github/copilot/` 的 wrapper 原則
- [ ] 定義哪些內容可由 wrapper 重述，哪些只能引用 canonical source
- [ ] 決定是否需要 generator / sync scripts

## Stage 4: Pilot Migration

- [ ] 選定第一個 skill pilot
- [ ] 選定第一組 command prompt pilot
- [ ] 建立 pilot canonical source
- [ ] 建立 pilot wrapper mapping
- [ ] 驗證 guide / canonical / wrapper 三層一致
- [ ] 記錄 migration lesson learned

## Stage 5: Rollout Decision

## Stage 5: Rollout

- [ ] 建立 canonical source 根目錄
- [ ] 建立至少一個 skill wrapper pilot
- [ ] 建立至少一組 command wrapper pilot
- [ ] 更新 `.ai/` / `.dev/` / wrapper 相關索引
- [ ] 補齊新增與維護規則

## Stage 6: Local Sync And Follow-Up

- [ ] 提供 Codex 本機同步 / 安裝語法
- [ ] 明確記錄 Claude / Codex / Gemini / GitHub Copilot 的 wrapper 路徑
- [ ] 記錄 pilot migration 的 lessons learned
- [ ] 決定後續是否導入 generated wrapper strategy

## Stage 7: Command To Skill Convergence

- [x] 確認 `.codex/commands/` 已移除且無活躍引用
- [x] 完成 `.ai/assets/commands/` 退役並改以 sub-agent-role-prompts 承接
- [x] 分類 `.ai/assets/` 中 command-style vs shared / explanatory materials
- [x] 為 command-style prompts 定義正確的 sub-agent-role / shared migration target
- [x] 定義需保留的 shared / explanatory prompt materials 長期放置策略
- [x] 將 canonical skill references 從 `.claude/skills/.../references/` 遷移到 `.ai/assets/skills/.../references/`
- [x] 更新 strategy docs 與 indexes，改為 skill-first、command-retirement wording



# Stage F Remove Codex Prompts

本階段移除 `.codex/prompts/`，因為 repo 已改以 `.ai/` canonical assets 加上 `.codex/skills/` runtime wrappers 為主，不再保留額外的 Codex prompt wrapper 層。

## Completed

- 刪除 `.codex/prompts/` 下的 wrapper files
- 移除 canonical metadata 中對 Codex prompt wrappers 的映射
- 更新索引與策略文件，改以 `.codex/skills/` 為 Codex 唯一 wrapper 入口

## Outcome

目前 Codex 在 repo 內的正式入口為：

- `.codex/skills/`

而目前的 canonical routing 已收斂為：

- top-level capabilities 使用 `.ai/assets/skills/`
- delegated worker-role assets 使用 `.ai/assets/sub-agent-role-prompts/`
- reusable prompt materials 保留在 `.ai/assets/`

`.ai/assets/commands/` 已於後續清理階段自 repo 移除。


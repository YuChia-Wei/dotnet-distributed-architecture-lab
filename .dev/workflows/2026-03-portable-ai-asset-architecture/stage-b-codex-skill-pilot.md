# Stage B Codex Skill Pilot

本階段為 `ddd-ca-hex-architect` 建立第一個 Codex runtime skill wrapper pilot。

## Completed

- 建立 `.codex/skills/ddd-ca-hex-architect/SKILL.md`
- 建立 runtime-wrapper-local 的薄指標 references
- 更新 canonical skill metadata，記錄 Codex prompt wrapper 與 runtime wrapper 的差異

## Outcome

目前 `ddd-ca-hex-architect` 已同時具備：

- canonical source
  - `.ai/assets/skills/ddd-ca-hex-architect/skill.yaml`
- Codex prompt wrapper
  - `.codex/prompts/ddd-ca-hex-architect.md`
- Codex runtime skill wrapper
  - `.codex/skills/ddd-ca-hex-architect/SKILL.md`

這讓 repo 內可以同時支援：

- prompt-style usage
- runtime skill-style usage

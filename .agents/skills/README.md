# Agents Skill Wrappers

本目錄放置目前 repo 內給 Codex / agent runtime 使用的 skill wrapper。

## 角色

- `.agents/skills/`
  - runtime wrapper root
- `.ai/assets/skills/`
  - canonical skill registry 與單一真相
- `.dev/guides/ai-collaboration-guides/`
  - human-facing guides

## 使用方式

1. 先到 `.ai/assets/skills/README.MD` 找完整 skill registry。
2. 再看對應 `skill.yaml` 確認 canonical purpose、inputs、outputs、constraints、wrapper targets、human guide。
3. 需要目前 runtime 可讀入口時，再使用 `.agents/skills/<skill>/SKILL.md` wrapper。

## Wrapper 原則

- wrapper 不應成為 skill 規則的單一真相
- 新增 skill 時，應先補 canonical spec，再補 runtime wrapper
- 若 canonical spec 與 wrapper 衝突，以 `.ai/assets/skills/` 為準
- 每個 wrapper `SKILL.md` 應只保留 canonical spec、human guide、references、runtime-specific metadata 的薄入口

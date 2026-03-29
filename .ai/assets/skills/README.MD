# Skill Specs

本目錄放置中立的 `skill-spec` 定義，不依賴特定 agent runtime。

## 建議結構

```text
.ai/assets/skills/<skill-id>/
  skill.yaml
  prompts/
  references/
  examples/
```

## 最小原則

- `skill.yaml` 是 canonical entry
- `prompts/` 放 skill 直接依賴的 prompt packages
- `references/` 放中立參考資料
- `examples/` 放可攜示例

## 不應放在這裡的內容

- agent-specific metadata
- Claude / Codex / Gemini / Copilot runtime instructions
- human-facing tutorial text

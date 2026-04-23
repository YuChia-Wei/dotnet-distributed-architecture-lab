# Skill Specs

本目錄放置中立的 `skill-spec` 定義，不依賴特定 agent runtime。
這裡是完整 skill registry 與單一真相。

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

## Canonical Registry

目前 canonical skill registry 包含：

- `bdd-gwt-test-designer`
- `code-reviewer`
- `command-use-case-implementer`
- `ddd-ca-hex-architect`
- `problem-frame-author`
- `query-use-case-implementer`
- `repo-structure-sync`
- `requirement-author`
- `reactor-implementer`
- `spec-author`
- `spec-compliance-validator`
- `staged-refactor-implementer`
- `tactical-refactor-implementer`

## 與 Wrapper 的關係

- `.ai/assets/skills/README.MD`
  - 完整 skill registry
- `.dev/guides/ai-collaboration-guides/README.MD`
  - human-facing skill guides
- `.agents/skills/README.md`
  - current runtime wrapper index
- `.claude/skills/README.md`
  - Claude-compatible wrapper index

當 canonical spec 與 wrapper 發生衝突時，以本目錄為準。

## 不應放在這裡的內容

- agent-specific metadata
- Claude / Codex / Gemini / Copilot runtime instructions
- human-facing tutorial text
